import argparse
import json
from kconfiglib import *
import sys
import pathlib
import os


def main(args):
    debugger = args.debugger
    imagePath = pathlib.Path(os.path.abspath(args.image_path)).as_posix()
    buildDir = pathlib.Path(os.path.dirname(args.image_path)).as_posix()
    ws = args.workspace
    os.environ["srctree"] = ws

    # get the target platform from kconfig
    kconf = Kconfig(f"{ws}/Kconfig", suppress_traceback=True)
    kconf.load_config(f"{buildDir}/.config")

    platform = ""
    for c in kconf.unique_choices:
        if c.name == "PLATFORM":
            choice = c.user_selection
            choiceName = choice.name

            if choiceName == "PLATFORM_MSS":
                platform = "mss"
            elif choiceName == "PLATFORM_MIV":
                platform = "miv"
            elif choiceName == "PLATFORM_MPS":
                platform = "mps"
            elif choiceName == "PLATFORM_VPB":
                platform = "vpb"
            else:
                print(f"No platform selected in configuration")
                sys.exit(1)

    # read the launch config template files and extract the relevant templates
    with open(
        os.path.join(ws, "sdk/tools/templates/launchConfigs/configs.json"), "r"
    ) as fPlatformConfigs:
        platformConfigs = json.load(fPlatformConfigs)
        platformConfig = platformConfigs[debugger][platform]

    debuggerTemplateName = debugger
    if "flashpro" in debuggerTemplateName:
        debuggerTemplateName = "flashpro"
    
    with open(
        os.path.join(ws, "sdk/tools/templates/launchConfigs", f"{debuggerTemplateName}.json"), "r"
    ) as fDebuggerConfig:
        debuggerConfig = json.load(fDebuggerConfig)

    # insert the platform config data into the debug config template
    for key in platformConfig:
        debuggerConfig[key] = platformConfig[key]

    debuggerConfig["program"] = imagePath
    debuggerConfig["miDebuggerArgs"] = "-se " + imagePath
    fileName, fileExtension = os.path.splitext(os.path.basename(imagePath))

    if args.name == "":
        buildDirBase = os.path.basename(os.path.normpath(buildDir))
        debuggerConfig["name"] = buildDirBase + "-" + fileName + "-" + debugger
    else:
        debuggerConfig["name"] = args.name

    # do some string replacement for renode configurations
    configString = json.dumps(debuggerConfig, indent=4)
    if debugger == "renode":
        configString = configString.replace("${PATH_TO_IMAGE}", debuggerConfig["program"])
        configString = configString.replace("${TARGET_BOARD}", args.board)
    debuggerConfig = json.loads(configString)

    if not args.output:
        args.output = ".vscode/launch.json"

    if not os.path.exists(args.output):
        os.makedirs(os.path.dirname(args.output), exist_ok=True)

        launchJsonData = {"configurations": [debuggerConfig]}
    else:
        with open(args.output, "r") as fLaunchJson:
            launchJsonData = json.load(fLaunchJson)
            launchJsonData["configurations"].append(debuggerConfig)

    with open(args.output, "w") as fLaunchJson:
        json.dump(launchJsonData, fLaunchJson, indent=4)


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
        "-g",
        "--debugger",
        type=str,
        choices=[
            "embedded-flashpro-5", 
            "embedded-flashpro-6", 
            "flashpro-5", 
            "flashpro-6", 
            "olimex-tiny-h", 
            "renode"
        ],
        help="Choose the debugger you are using",
    )

    parser.add_argument(
        "-i",
        "--image-path",
        type=str,
        help="Enter the path to the image",
    )

    parser.add_argument("-n", "--name", type=str, default="")

    parser.add_argument(
        "-b",
        "--board",
        type=str,
        choices=[
            "curiosity-pic64-GX"
        ],
        help="Choose a board to emulate with Renode",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Choose an output file for your debug configuration",
    )

    args = parser.parse_args()
    main(args)
