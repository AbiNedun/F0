{
    description = "F0";

    inputs = {
        # nixpkgs.url = "nixpkgs/nixos-25.05";
        nixpkgs.url = "github:vaisriv/nixpkgs";

        flake-utils = {
            url = "github:numtide/flake-utils";
        };
    };

    outputs = inputs @ {
        self,
        nixpkgs,
        flake-utils,
        ...
    }:
        flake-utils.lib.eachDefaultSystem (
            system: let
                pkgs = import nixpkgs {
                    inherit system;
                    config.allowUnfree = false; # set to true if we need a package that is not free (as in libre)
                };
            in {
                formatter = pkgs.alejandra;

                devShells.default = pkgs.mkShell {
                    packages = with pkgs; [
                        # python
                        (python3.withPackages (ps:
                            with ps; [
                                # python packages here
                                tkinter
                                fastf1
                            ]))
                        basedpyright
                        ruff
                    ];
                };

                packages = {
                    default = self.packages.${system}.F0;

                    F0 = pkgs.python3Packages.buildPythonApplication {
                        pname = "F0";
                        version = "0.1.0";
                        pyproject = true;

                        src = ./.;

                        nativeBuildInputs = with pkgs.python3Packages; [
                            hatchling
                            hatch-vcs
                        ];

                        propagatedBuildInputs = with pkgs.python3Packages; [
                            tkinter
                            fastf1
                        ];

                        meta = with pkgs.lib; {
                            description = "F0 is a circuit and telemetry tracker for F1 Grandprix.";
                            mainProgram = "F0";
                            license = licenses.mit;
                            homepage = "https://github.com/abinedun/F0";
                            changelog = "https://github.com/abinedun/F0/releases/tag/v${version}";
                            maintainers = with maintainers; [
                                # abinedun
                                vaisriv
                            ];
                        };
                    };
                };
            }
        );
}
