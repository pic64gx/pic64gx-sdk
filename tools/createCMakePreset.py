import argparse
import os
import json
import sys
import pathlib

def createCMakePreset(
    workspace_base,
    board,
    app_dir,
    build_dir,
    c_flags,
    asm_flags,
    cxx_flags,
    preset_name,
    preset_display,
    project_name,
    build_type=None
):
    workspace_base = pathlib.Path(workspace_base).as_posix()
    preset_file_path = os.path.join(app_dir, "CMakePresets.json")

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

    abs_app_dir = pathlib.Path(os.path.abspath(app_dir)).as_posix()
    format_app_dir = abs_app_dir.replace(workspace_base, "${sourceDir}")

    abs_board_dir = pathlib.Path(os.path.abspath(board)).as_posix()
    format_board_dir = abs_board_dir.replace(workspace_base, "${sourceDir}")

    preset = {
        "name": preset_name,
        "displayName": preset_display,
        "inherits": "default",
        "binaryDir": build_dir,
        "cacheVariables": {
            "APP_DIR": format_app_dir,
            "PROJECT_NAME": project_name,
            "BOARD": format_board_dir,
            "EXTRA_C_FLAGS": c_flags,
            "EXTRA_CXX_FLAGS": cxx_flags,
            "EXTRA_ASM_FLAGS": asm_flags,
        },
    }

    if build_type:
        preset["cacheVariables"]["CMAKE_BUILD_TYPE"] = build_type

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
    createCMakePreset(
        args.workspace_base,
        args.board,
        args.app_dir,
        args.build_dir,
        args.c_flags,
        args.asm_flags,
        args.cxx_flags,
        args.preset_name,
        args.preset_display,
        args.project_name,
        args.build_type
    )

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
        help="the output build directory. defaults to nothing",
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
        "--project-name",
        type=str,
        default="",
        help="set the name of the project to be built by this preset"
    )

    parser.add_argument(
        "--build-type",
        type=str,
        choices=["Release", "Debug"],
        default=""
    )

    args = parser.parse_args()
    main(args)
