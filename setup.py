#!/usr/bin/env python3

# Copyright (c) 2014 Marco Schindler
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.

from setuptools import setup

from btrfs_pnbackup import __version__

setup(
    name='btrfs-pnbackup',
    version=__version__,
    python_requires=">=3.8",
    author='Marco Schindler',
    author_email='masc@disappear.de',
    maintainer='Will Brown',
    maintainer_email='5326080+wpbrown@users.noreply.github.com',
    license='GNU GPL',
    url='https://github.com/wpbrown/btrfs-pnbackup',
    packages=['btrfs_pnbackup'],
    description='A fork of btrfs-sxbackup. Incremental btrfs snapshot backups with push/pull support via SSH.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: Utilities'],

    entry_points={
        'console_scripts': ['btrfs-pnbackup = btrfs_pnbackup.__main__:main']
    }
)
