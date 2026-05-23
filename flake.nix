{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python3
            pkgs.python3Packages.pip
            pkgs.python3Packages.setuptools
            pkgs.python3Packages.wheel
            pkgs.python3Packages.pytest
            pkgs.python3Packages.pygments
            pkgs.python3Packages.build

            pkgs.ffmpeg
            pkgs.rclone
            pkgs.gitleaks

            pkgs.podman
          ];
          shellHook = ''
            if [ ! -d "env" ]; then
              virtualenv env
            fi

            source env/bin/activate

            export PIP_DISABLE_PIP_VERSION_CHECK=1
            export PYTHONPATH=$PWD/src:$PYTHONPATH

            if [ requirements.txt -nt env/.pip_installed ]; then
              python -m pip install --upgrade pip
              python -m pip install -r requirements.txt
              touch env/.pip_installed
            fi
          '';
        };
      });
}