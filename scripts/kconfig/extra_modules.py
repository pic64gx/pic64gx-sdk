import argparse
import os
import sys

def main(args):
    print("Assembling Kconfig file for the extra modules")

    module_list = args.modules.split(";")

    with open(f"{args.build_dir}/Kconfig.modules", "w") as f:
        for module in module_list:
            module_path = f"{module}/Kconfig"

            if not os.path.isdir(module):
                sys.exit(f"Extra module {module} is an invalid path")
            else:
                if os.path.exists(module_path):
                    f.write(f"source \"{module_path}\" \n")

if __name__ == "__main__":
    parser= argparse.ArgumentParser()

    parser.add_argument(
        "-m",
        "--modules",
        type=str
    )

    parser.add_argument(
        "-d",
        "--build-dir",
        type=str
    )

    args = parser.parse_args()

    main(args)