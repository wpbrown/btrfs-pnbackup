rec {
  description = "Incremental btrfs snapshot backups with push/pull support via SSH.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      meta = {
        inherit description;
        homepage = "https://github.com/wpbrown/btrfs-pnbackup";
        license = pkgs.lib.licenses.gpl2Plus;
        platforms = pkgs.lib.platforms.linux;
      };
    in
    {
      packages.${system}.default = pkgs.python3Packages.buildPythonApplication {
        inherit meta;

        pname = "btrfs-pnbackup";
        version = "0.7.1";
        pyproject = true;

        src = builtins.path {
          path = ./.;
          name = "source";
        };

        dependencies = with pkgs.python3Packages; [
          distutils
        ];

        build-system = [ pkgs.python3Packages.setuptools ];
      };

      apps.${system}.default = {
        inherit meta;
        
        type = "app";
        program = "${self.packages.${system}.default}/bin/btrfs-pnbackup";
      };

      devShells.${system}.default = pkgs.mkShell {
        inputsFrom = [ self.packages.${system}.default ];
      };
    };
}
