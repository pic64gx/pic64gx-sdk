import argparse
import json
import os
from kconfiglib import *


def applyConfig(args):
    config = json.loads(args.config)

    os.environ["srctree"] = args.workspace
    os.environ["KCONFIG_APP_DIR"] = args.app_dir
    os.environ["KCONFIG_BINARY_DIR"] = args.build_dir

    kconf = Kconfig(f"{args.workspace}/Kconfig", warn_to_stderr=False, suppress_traceback=True)
    kconf.load_config()

    for key in config:
        value = config[key]

        # print(key, value)
        if value == True:
            value = "y"
        elif value == False:
            value = "n"

        try:
            sym = kconf.syms[key]
            sym.set_value(value)
        except:
            pass

    header = """/*
auto generated header
*/
#ifndef AUTOCONF_H
#define AUTOCONF_H\n"""

    print(kconf.write_autoconf(f"{args.build_dir}/autoconf.h", header))

    with open(f"{args.build_dir}/autoconf.h", "a") as autoconf:
        autoconf.write("#endif\n")
        autoconf.close()

    print(kconf.write_config(f"{args.build_dir}/.config"))

    os.unsetenv("srctree")


def main(args):
    applyConfig(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    workspace = os.getcwd()
    parser.add_argument(
        "-w",
        "--workspace",
        type=str,
        default=workspace,
        help="""Path to the base directory of the workspace. If left empty this
variable will automatically be set to the current working directory of this
script""",
    )

    parser.add_argument(
        "-a",
        "--app-dir",
        type=str,
        default="",
        help="Path to the application directory",
    )

    parser.add_argument(
        "-d",
        "--build-dir",
        type=str,
        default="",
        help="build directory for the project",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="json",
        default=".config configuration settings",
    )

    args = parser.parse_args()
    main(args)
