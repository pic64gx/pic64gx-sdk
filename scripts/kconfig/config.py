from kconfiglib import *
import os
import sys
import argparse

sys.path.append(f"modules/kconfiglib")
from menuconfig import menuconfig
# from guiconfig import menuconfig as guiconfig


def generate_autoconf(kconf, output_dir, cmake_flag):
    header = """/*
auto generated header
*/
#ifndef AUTOCONF_H
#define AUTOCONF_H\n"""

    print(kconf.write_autoconf(f"{output_dir}autoconf.h", header))

    with open(f"{output_dir}autoconf.h", "a") as autoconf:
        autoconf.write("#endif\n")
        autoconf.close()

    if cmake_flag:
        # Write the new configuration settings into .config, the previous
        # settings are written to .config.old
        print(kconf.write_config(f"{output_dir}.config"))


def main(args):
    os.environ["srctree"] = args.workspace_base
    os.environ["KCONFIG_BINARY_DIR"] = args.build_dir
    os.environ["KCONFIG_APP_DIR"] = args.app_dir

    try:
        # read the Kconfig file tree
        kconf = Kconfig(f"{args.workspace_base}/Kconfig", warn_to_stderr=False)
    except Exception as err:
        sys.stderr.write(str(err))
        sys.exit(1)

    # if this script is being run by the automated cmake build system
    if args.cmake:
        # load the settings from the config file to be converted into autoconf.h
        kconf.load_config(args.config_file)
        output_dir = args.build_dir + "/"
    # if this script is being run by a user
    else:
        os.chdir(args.build_dir)
        # menuconfig() reads the .config file from the script's current working
        # directory and then displays the GUI with the settings from .config.
        # On exit menuconfig saves the new settings into the kconf object to be
        # converted into autoconf.h. It also writes the new config to .config
        # and saves the old config in .config.old
        # if args.guiconfig:
        #     guiconfig(kconf)
        # else:
        menuconfig(kconf)
        output_dir = ""

    generate_autoconf(kconf, output_dir, args.cmake)

    os.unsetenv("srctree")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="config",
        description="""Read config files, display Kconfig GUI and generate an
autoconf.h file""",
        epilog="",
    )

    workspace_base = os.getcwd()

    parser.add_argument(
        "-w",
        "--workspace-base",
        type=str,
        default=workspace_base,
        help="""Path to the base directory of the workspace. If left empty this
variable will automatically be set to the current working directory of this
script""",
    )

    parser.add_argument(
        "-c",
        "--config-file",
        type=str,
        default="",
        help="""Path to the .config or proj.conf file. This argument can be
ignored if if the config file is located in the base level of the build
directory""",
    )

    parser.add_argument(
        "-d", "--build-dir", type=str, default="", help="Path to the build directory"
    )

    parser.add_argument(
        "-m",
        "--cmake",
        action="store_true",
        help="""Set this flag if this script is being run by the automated CMake 
build system. Ignore this flag if the script is being run by a user""",
    )

    parser.add_argument("-a", "--app-dir", help="""Path to the application directory""")

#     parser.add_argument(
#         "-g",
#         "--guiconfig",
#         action="store_true",
#         help="""Set this flag to use guiconfig instead of the menuconfig
# interface""",
#     )

    args = parser.parse_args()

    main(args)
