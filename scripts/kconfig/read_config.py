from kconfiglib import *
import argparse


def main(args):
    kconf = Kconfig("./Kconfig")

    kconf.load_config(f"{args.build_dir}/.config")

    for symbol in kconf.unique_defined_syms:
        val = symbol.str_value

        if symbol.type == BOOL:
            if val == "y":
                val = "ON"
            elif val == "n":
                continue
            else:
                continue

        elif symbol.type == STRING:
            val = f"\"{val}\""
        else:
            continue
            
        print(f"CONFIG_{symbol.name} {val};", end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--build-dir",
        type=str,
        help="""the path to the build directory"""
    )

    args = parser.parse_args()
    main(args)