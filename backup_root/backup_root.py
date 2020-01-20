#!/usr/bin/env python3
import argparse
import pathlib
import os.path
import os
import configparser
from enum import Enum
from typing import Sequence


class RootPermissionError(Exception):
    def __init__(self):
        pass


class ConfigurationError(Exception):
    def __init__(self):
        pass


class PathCheckMode(Enum):
    ExactOrSubPath = 1
    SubPathOnly = 2


class Authorization:
    __CONFIG_FILENAME = '/etc/backup_root.conf'

    def __init__(self, config_file: str = __CONFIG_FILENAME):
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
        except:
            raise ConfigurationError()

        self._user = os.environ['SUDO_USER']
        if self._user not in config:
            raise Exception('User is not granted any access.')

        self._allowed_root = pathlib.Path(config[self._user]['allowed_path']).resolve()

    def path_allowed(self, path: pathlib.Path, mode: PathCheckMode = PathCheckMode.SubPathOnly) -> bool:
        # In Python 3.6 we could use resolve(strict=False), but for now we have to go back to os.path.
        required_parts = self._allowed_root.parts
        requested_parts = pathlib.Path(os.path.realpath(str(path))).parts
        if required_parts != requested_parts[:len(required_parts)]:
            return False
        if mode == PathCheckMode.SubPathOnly and len(requested_parts) == len(required_parts):
            return False

        return True

    def assert_path_allowed(self, path: pathlib.Path, mode: PathCheckMode = PathCheckMode.SubPathOnly) -> None:
        if not self.path_allowed(path, mode):
            raise RootPermissionError()


def run(args: Sequence[str] = None):
    os.execvp(args[0], args)


def cmd_mv(auth: Authorization, args: argparse.Namespace):
    auth.assert_path_allowed(args.source)
    auth.assert_path_allowed(args.destination)
    return ('mv', str(args.source), str(args.destination))


def cmd_btrfs_subvolume_create(auth: Authorization, args: argparse.Namespace):
    auth.assert_path_allowed(args.target)
    return ('btrfs', 'subvolume', 'create', str(args.target))


def cmd_btrfs_subvolume_delete(auth: Authorization, args: argparse.Namespace):
    for target in args.target:
        auth.assert_path_allowed(target)
    return ('btrfs', 'subvolume', 'delete', *(str(target) for target in args.target))


def cmd_btrfs_subvolume_show(auth: Authorization, args: argparse.Namespace):
    auth.assert_path_allowed(args.target, PathCheckMode.ExactOrSubPath)
    return ('btrfs', 'subvolume', 'show', str(args.target))


def cmd_btrfs_receive(auth: Authorization, args: argparse.Namespace):
    auth.assert_path_allowed(args.target, PathCheckMode.ExactOrSubPath)
    return ('btrfs', 'receive', '--chroot', str(args.target))


def cmd_btrfs_subvolume_list(auth: Authorization, args: argparse.Namespace):
    auth.assert_path_allowed(args.list_path, PathCheckMode.ExactOrSubPath)
    return ('btrfs', 'subvolume', 'list', '-o', str(args.list_path))


def main():
    # Setup parser
    cmd_parser = argparse.ArgumentParser()
    cmd_subparsers = cmd_parser.add_subparsers()

    mv_parser = cmd_subparsers.add_parser('mv')  # type: argparse.ArgumentParser
    mv_parser.add_argument('source', type=pathlib.Path)
    mv_parser.add_argument('destination', type=pathlib.Path)
    mv_parser.set_defaults(func=cmd_mv)

    btrfs_parser = cmd_subparsers.add_parser('btrfs')  # type: argparse.ArgumentParser
    btrfs_subparsers = btrfs_parser.add_subparsers()
    btrfs_subvolume_parser = btrfs_subparsers.add_parser('subvolume', aliases=['sub'])  # type: argparse.ArgumentParser
    btrfs_subvolume_subparsers = btrfs_subvolume_parser.add_subparsers(dest='subcommand')
    btrfs_subvolume_create_parser = btrfs_subvolume_subparsers.add_parser('create')
    btrfs_subvolume_create_parser.add_argument('target', type=pathlib.Path)
    btrfs_subvolume_create_parser.set_defaults(func=cmd_btrfs_subvolume_create)
    btrfs_subvolume_delete_parser = btrfs_subvolume_subparsers.add_parser('delete', aliases=['del'])
    btrfs_subvolume_delete_parser.add_argument('target', type=pathlib.Path, nargs='+')
    btrfs_subvolume_delete_parser.set_defaults(func=cmd_btrfs_subvolume_delete)
    btrfs_subvolume_show_parser = btrfs_subvolume_subparsers.add_parser('show')
    btrfs_subvolume_show_parser.add_argument('target', type=pathlib.Path)
    btrfs_subvolume_show_parser.set_defaults(func=cmd_btrfs_subvolume_show)

    btrfs_subvolume_list_parser = btrfs_subvolume_subparsers.add_parser('list')
    btrfs_subvolume_list_parser.add_argument('-o', dest='list_path', type=pathlib.Path, required=True)
    btrfs_subvolume_list_parser.set_defaults(func=cmd_btrfs_subvolume_list)

    btrfs_receive_parser = btrfs_subparsers.add_parser('receive')
    btrfs_receive_parser.add_argument('-C', '--chroot')
    btrfs_receive_parser.add_argument('target', type=pathlib.Path)
    btrfs_receive_parser.set_defaults(func=cmd_btrfs_receive)

    btrfs_version_parser = btrfs_subparsers.add_parser('version')
    btrfs_version_parser.set_defaults(func=lambda _,__: ('btrfs', 'version'))

    # Check usage
    if os.geteuid() != 0 or 'SUDO_USER' not in os.environ:
        cmd_parser.error("backup_root is only meant to be run as root via sudo.")

    # Execute
    authorization = Authorization()
    args = cmd_parser.parse_args()
    if not hasattr(args, 'func'):
        cmd_parser.print_usage()
        cmd_parser.exit(1)

    cmd_args = args.func(authorization, args)
    run(cmd_args)


main()
