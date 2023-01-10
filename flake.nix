{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, flake-utils, nixpkgs }:
    {
      overlays.default = final: prev: {
        inherit (self.packages.${prev.system}) catgpt;
      };

      nixosModules.default = ./nixos-module.nix;
    } // flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        packages.catgpt = with pkgs;
          stdenvNoCC.mkDerivation {
            pname = "year-of-bot";
            version = "0.1.0";

            src = ./.;

            buildInputs = [
              (python3.buildEnv.override {
                extraLibs = [ python3Packages.aiohttp python3Packages.yarl ];
              })
            ];

            installPhase = ''
              mkdir -p $out/bin
              cp -r * $out/bin
              chmod +x $out/bin/catgpt.py
            '';

            verifyPhase = ''
              $out/bin/catgpt.py verify
            '';

            meta = {
              description = "A Pleroma bot that mews at you.";
              mainProgram = "catgpt.py";
              license = lib.licenses.agpl3Only;
            };
          };

        packages.default = self.packages.${system}.catgpt;

        devShells.default = with pkgs;
          mkShell {
            buildInputs = [ python3Packages.aiohttp python3Packages.yarl ];
          };
      });
}
