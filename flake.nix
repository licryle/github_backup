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
            pkgs.python3Packages.virtualenv

            pkgs.ffmpeg
            pkgs.rclone
          ];
          shellHook = ''
            if [ ! -d "env" ]; then
              virtualenv env
            fi

            source env/bin/activate

            export PIP_DISABLE_PIP_VERSION_CHECK=1

            python -m pip install --upgrade pip

            if [ -f requirements.txt ]; then
              python -m pip install -r requirements.txt
            fi
          '';
        };
      });
}