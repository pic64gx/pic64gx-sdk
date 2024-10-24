import argparse
import os
import shutil
import json
import glob
from createProjConf import initProjConf


def checkDepends(key, config):
    # run through the list of depends on for the symbol. if all symbols that
    # this symbol depends on are not active then don't activate this symbol
    allowConfig = False

    deps = config[key]["dependsOn"]
    if len(deps) == 0:
        return True

    for d in config[key]["dependsOn"]:
        if d == "y":
            allowConfig = True

    return allowConfig


def getProjectSourceFiles(platform):
    template_path = f"{os.environ['SDK_BASE']}/tools/templates/projects/{platform}"
    search_path = f"{template_path}/**/*.c"
    files = glob.glob(search_path, recursive=True)

    files_str = ""
    for f in files:
        stripped_path = f.replace(template_path, "${CMAKE_CURRENT_SOURCE_DIR}")
        sanitised_path = stripped_path.replace("\\", "/")
        files_str += "\t" + sanitised_path + "\n"

    return files_str


def initCMakeLists(dir, name, platform, add_src, add_inc):
    shutil.copy(f"{os.environ['SDK_BASE']}/tools/templates/CMakeLists.txt", dir)

    with open(f"{dir}/CMakeLists.txt", "r") as fr:
        data = fr.read()
        data = data.replace("${NAME}", name)
        if platform:
            data = data.replace(
                "${PROJECT_SOURCE_FILES}\n", getProjectSourceFiles(platform)
            )
        else:
            data = data.replace("${PROJECT_SOURCE_FILES}\n", "")

        additional_src_files = ""
        if len(add_src) > 0:
            for src in add_src:
                src = src.replace(dir, "${CMAKE_CURRENT_SOURCE_DIR}")
                additional_src_files += "\t" + src + "\n"
        data = data.replace("${ADDITIONAL_SOURCE_FILES}", additional_src_files)

        additional_inc_dirs = ""
        if len(add_inc) > 0:
            for inc in add_inc:
                inc = inc.replace(dir, "${CMAKE_CURRENT_SOURCE_DIR}")
                additional_inc_dirs += "\t" + inc + " \n"
        data = data.replace("${ADDITIONAL_INCLUDE_DIRECTORIES}\n", additional_inc_dirs)

    with open(f"{dir}/CMakeLists.txt", "w") as fw:
        fw.write(data)
    return


def initSrc(dir, platform):
    shutil.copytree(
        f"{os.environ['SDK_BASE']}/tools/templates/projects/{platform}/src",
        f"{dir}/src",
        dirs_exist_ok=True
    )


def getPlatform(config):
    if "PLATFORM_MSS" in config:
        return "mss"
    else:
        return None


def main(args):
    directory = args.directory
    name = args.name
    platform = getPlatform(args.config)
    add_src = args.additional_src
    add_inc = args.additional_include

    if not os.path.isdir(directory):
        os.makedirs(f"{directory}", exist_ok=True)

    initProjConf(directory, args.config)

    # Get the proj.conf template
    with open(f"{os.environ['SDK_BASE']}/tools/templates/proj.conf", 'r') as source_file:
        source_contents = source_file.read()

    # Append proj.conf template to the application proj.conf
    proj_config = os.path.join(directory,"proj.conf")

    with open(proj_config, 'a') as destination_file:
        destination_file.write(source_contents)

    initCMakeLists(directory, name, platform, add_src, add_inc)
    if platform:
        initSrc(directory, platform)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", "--name", type=str, default="new_project")

    parser.add_argument(
        "-d", "--directory", type=str, default="", help="directory for the new project"
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="json",
        default="proj.conf configuration settings",
    )

    parser.add_argument("-s", "--additional-src", nargs="*", default=[])

    parser.add_argument("-i", "--additional-include", nargs="*", default=[])

    args = parser.parse_args()
    main(args)
