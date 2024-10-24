import os
import subprocess
import argparse
import pathlib
import filecmp
import shutil
import json
import sys
import yaml
import re


def savePreviousBuildConfig(build_dir):
    src_config = f"{build_dir}/.config"
    dst_config = f"{build_dir}/.config.prev"
    if os.path.exists(src_config) and os.path.exists(dst_config):
        shutil.copyfile(src_config, dst_config)


# regen arg tells cmake to regenerate the autoconf file
# this only happens on a first time or a pristine build


def runCMake(sdk_base, workspace_base, board, args, regen=True):
    res = subprocess.run(
        [
            "cmake",
            f"-DWORKSPACE={workspace_base}",
            f"-DSDK_BASE={sdk_base}",
            f"-C {sdk_base}/cmake/preload.cmake",
            f"-DCMAKE_MODULE_PATH={sdk_base}/cmake",
            f"-DCMAKE_TOOLCHAIN_FILE={sdk_base}/cmake/cross-compiler-gcc-tc.cmake",
            f"-DBOARD={board}",
            f"-DREGEN={regen}",
            f"-DEXTRA_C_FLAGS={args.c_flags}",
            f"-DEXTRA_ASM_FLAGS={args.asm_flags}",
            f"-Wno-dev",
            f"-DEXTRA_CXX_FLAGS={args.cxx_flags}",
            "-Wno-dev",
            f"-S {args.app_dir}",
            f"-B {args.build_dir}",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
        ]
    )

    if res.returncode != 0:
        sys.exit(res.returncode)


def getProjectName(app_dir):
    clean_app_dir = app_dir.rstrip("/")
    clean_app_dir = clean_app_dir.rstrip("\\")
    return os.path.basename(clean_app_dir)


# reconfiguring cmake not only rebuilds the project but also updates the memory
# target, source files, etc. this happens on a first time build, a pristine
# build, and should also happen when the config file from the previous build
# does not match the current build config file
def shouldReconfigureCMake(build_dir):
    config_file = f"{build_dir}/.config"
    prev_build_config_file = f"{build_dir}/.config.prev"

    # the previous build config file is always generated when using this script
    # however when using presets it is not generated. if the previous build
    # config file does not exist then don't reconfigure cmake
    if not os.path.exists(prev_build_config_file):
        return True
    else:
        res = filecmp.cmp(config_file, prev_build_config_file)
        if res:
            return False
        else:
            return True


def getBuildError(build_dir):
    with open(os.path.join(build_dir, "CMakeFiles/CMakeConfigureLog.yaml")) as yml:
        log = yaml.safe_load(yml)

    message = []
    for event in log["events"]:
        try:
            lines = event["message"].splitlines()
            for i, l in enumerate(lines):
                if re.match("^\d+$", l):
                    if int(l) != 0:
                        try:
                            message.index(lines[i + 1])
                        except:
                            message.append(lines[i + 1])
        except:
            pass

    return "".join(message)


def generatePreset(project_name, args, workspace_base, abs_board_dir):
    preset_file_path = os.path.join(args.app_dir, "CMakePresets.json")

    try:
        with open(preset_file_path, "r") as preset_file:
            CMakePresets = json.load(preset_file)
    except:
        CMakePresets = {
            "version": 7,
            "cmakeMinimumRequired": {"major": 3, "minor": 20, "patch": 0},
            "include": ["$penv{SDK_BASE}/cmake/defaultPreset.json"],
            "configurePresets": [],
            "buildPresets": [],
        }

    preset_name = args.preset_name
    preset_display = args.preset_display

    if next(
        (
            item
            for item in CMakePresets["configurePresets"]
            if item["name"] == preset_name
        ),
        None,
    ):
        sys.stderr.write(f'A preset with name "{preset_name}" already exists')
        sys.exit(1)

    if not preset_name:
        sys.stderr.write("A preset name must be provided")
        sys.exit(1)

    if not preset_display:
        sys.stderr.write("A preset display name must be provided")
        sys.exit(1)

    abs_app_dir = pathlib.Path(os.path.abspath(args.app_dir)).as_posix()
    format_app_dir = abs_app_dir.replace(workspace_base, "${sourceDir}")

    format_board_dir = abs_board_dir.replace(workspace_base, "${sourceDir}")

    preset = {
        "name": preset_name,
        "displayName": preset_display,
        "inherits": "default",
        "binaryDir": args.build_dir,
        "cacheVariables": {
            "APP_DIR": format_app_dir,
            "PROJECT_NAME": project_name,
            "BOARD": format_board_dir,
            "EXTRA_C_FLAGS": args.c_flags,
            "EXTRA_CXX_FLAGS": args.cxx_flags,
            "EXTRA_ASM_FLAGS": args.asm_flags,
        },
    }

    build_preset = {"name": preset_name, "configurePreset": preset_name}

    with open(preset_file_path, "w") as preset_file:
        if "configurePresets" in CMakePresets:
            CMakePresets["configurePresets"].append(preset)
        else:
            CMakePresets["configurePresets"] = [preset]

        if "buildPresets" in CMakePresets:
            CMakePresets["buildPresets"].append(build_preset)
        else:
            CMakePresets["buildPresets"] = [build_preset]
        
        json.dump(CMakePresets, preset_file, indent=4)


def main(args):
    if args.clean:
        try:
            shutil.rmtree(args.build_dir)
        except Exception as e:
            print(e)

    workspace_base = pathlib.Path(args.workspace_base).as_posix()

    sdk_base = pathlib.Path(os.path.join(workspace_base, "sdk")).as_posix()

    # if a preset isn't being called we need to establish these variables
    if not args.preset:
        project_name = getProjectName(args.app_dir)
        abs_build_dir = os.path.join(workspace_base, args.build_dir)
        dot_config_exists = os.path.exists(os.path.join(abs_build_dir, ".config"))
        board = pathlib.Path(os.path.abspath(args.board)).as_posix()
    else:
        abs_build_dir = None

    build_command = ["cmake", "--build", f"{args.build_dir}", "-j", "8"]

    if args.generate_preset:
        generatePreset(project_name, args, workspace_base, board)

    if args.preset:
        res = subprocess.run(["cmake", "--preset", args.preset])

        if res.returncode != 0:
            sys.exit(res.returncode)

        build_command = ["cmake", "--build", "--preset", args.preset]

    # on a pristine or a first time build cmake needs to run the configuration
    # step. the default value of true for the argument regen for the function
    # runCMakeLinux/runCMakeWindows is used. this tells cmake to generate the
    # autoconf file. on subsequent builds cmake may not need to reconfigure.
    # this is dependent on whether or not autoconf has been changed by the user
    # calling the config script. if autoconf has been updated, cmake
    # reconfigures with the updates from autoconf
    elif args.pristine == True or not dot_config_exists:
        runCMake(sdk_base, workspace_base, board, args)
        build_command.append("--clean-first")

    else:
        reconf = shouldReconfigureCMake(abs_build_dir)
        if reconf or args.no_build:
            runCMake(sdk_base, workspace_base, board, args, False)

    if not args.no_build:
        res = subprocess.run(build_command)

        if res.returncode != 0:
            if not abs_build_dir:
                sys.stderr.write("Undetermined error")
                sys.exit(res.returncode)

            error = getBuildError(abs_build_dir)

            if error == "":
                error = "Undetermined error, please check your project configuration settings are correct"

            sys.stderr.write(error)
            sys.exit(res.returncode)

    savePreviousBuildConfig(args.build_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    workspace_base = os.getcwd()

    parser.add_argument(
        "-w", "--workspace-base", type=str, default=workspace_base, help=""
    )

    parser.add_argument(
        "-b",
        "--board",
        type=str,
        default="",
        help="""the path to the target board the application is built for, ex:
./boards/icicle-kit-es""",
    )

    parser.add_argument(
        "-a",
        "--app-dir",
        type=str,
        help="the application to compile, ex: mss/mss_gpio/mpfs-gpio-interrupt",
    )

    parser.add_argument(
        "-d",
        "--build-dir",
        type=str,
        default="build",
        help="the output build directory. defaults to nothing",
    )

    parser.add_argument(
        "-p",
        "--pristine",
        action="store_true",
        help="""clean, non cached build of the application. does not delete the
    build directory before building""",
    )

    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="delete the build directory before building",
    )

    parser.add_argument(
        "-v",
        "--vectors",
        action="store_true",
        help="this project requires a toolchain with vector support",
    )

    parser.add_argument(
        "-cf",
        "--c-flags",
        type=str,
        default="",
        help="""additional c compiler flags. An equals sign must be used between
    argument and value eg. -cf=\"-Wall\"""",
    )

    parser.add_argument(
        "-af",
        "--asm-flags",
        type=str,
        default="",
        help="""additional assembly compiler flags. An equals sign must be used
        between argument and value eg. -af=\"-Wall\"""",
    )

    parser.add_argument(
        "-xf",
        "--cxx-flags",
        type=str,
        default="",
        help="""additional c++ compiler flags. An equals sign must be used
        between argument and value eg. -xf=\"-Wall\"""",
    )

    parser.add_argument(
        "--no-build",
        action="store_true",
        help="the script should only configure the project",
    )

    parser.add_argument(
        "--generate-preset",
        action="store_true",
        default=False,
        help="""generate a build preset using these arguments""",
    )

    parser.add_argument(
        "--preset-name",
        type=str,
        default="",
        help="""set the name of the preset generated with the --generate-preset
        argument eg. --preset-name=\"test preset\"""",
    )

    parser.add_argument(
        "--preset-display",
        type=str,
        default="",
        help="""set the display name of the preset generated with the --generate-preset
        argument eg. --preset-display=\"Test Preset\"""",
    )

    parser.add_argument(
        "--preset",
        type=str,
        help="""select a preset to build eg. --preset=\"test preset\"""",
    )

    args = parser.parse_args()
    main(args)
