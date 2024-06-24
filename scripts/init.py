import json
import os
import subprocess
import sys
from git import Repo
import tarfile
import zipfile
import urllib.request
import shutil
import pathlib
import argparse


def getUrl(module, sys_platform):
    if "url" in module:
        return module["url"]
    else:
        return module["os"][sys_platform]["url"]


def downloadExecutable(module, sys_platform):
    url = getUrl(module, sys_platform)
    file_name = os.path.split(url)[1]

    print(f"Downloading {file_name}...")
    with urllib.request.urlopen(url) as response, open(file_name, "wb") as out_file:
        data = response.read()
        out_file.write(data)

    print(f"Extracting...")
    if file_name.endswith(".tar.gz"):
        tar = tarfile.open(file_name, "r:gz")
        tar.extractall(module["path"])
        tar.close()
    elif file_name.endswith(".zip"):
        if sys_platform == "linux":
            subprocess.run(["unzip", "-uo", file_name, "-d", module["path"]])
        else:
            with zipfile.ZipFile(file_name, "r") as zip:
                zip.extractall(module["path"])

    if "parent_dirs" in module:
        unzipped_contents = os.listdir(module["path"])
        contents_dir = unzipped_contents[0]
        contents = os.listdir(f"{module['path']}/{contents_dir}")

        for file in contents:
            shutil.move(
                f"{module['path']}/{contents_dir}/{file}", f"{module['path']}/{file}"
            )


def downloadRepo(module, sys_platform):
    url = getUrl(module, sys_platform)
    print(f"Cloning repo {module['name']} into {module['path']}")
    Repo.clone_from(url, module["path"], no_checkout=True)

    checkRevision(module)


def checkRevision(module, ref=None):
    repo = Repo(module["path"])

    if ref:
        module_ref = ref
    elif module["ref"] == None:
        module_ref = repo.active_branch
    else:
        module_ref = module["ref"]

    print(f"Checking out revision {module_ref}")
    repo.remote().fetch()
    repo.git.checkout(module_ref)

    # check if the module ref is a branch or a specific commit
    for r in repo.remote().refs:
        # if the ref is a branch then pull new changes
        if f"origin/{module_ref}" == r.name:
            repo.remotes.origin.pull()


def installModule(module):
    sys_platform = sys.platform

    if not os.path.isdir(module["path"]):
        if module["type"] == "repo":
            downloadRepo(module, sys_platform)
        else:
            downloadExecutable(module, sys_platform)
    else:
        print(f"Module {module['name']} already exists in {module['path']}")
        if module["type"] == "repo":
            checkRevision(module)


def findManifestEntry(manifest, module_name):
    for key in manifest:
        if type(manifest[key]) == list:
            module = next(
                (item for item in manifest[key] if item["name"] == module_name), None
            )
            if module:
                return module
    return None


def main(args):
    with open("scripts/requirements/manifest.json", "r") as f:
        manifest = json.load(f)

    if args.update:
        for u in args.update:
            try:
                [module_name, ref] = u.split("@", 1)
            except:
                module_name = u
                ref = None

            if os.path.isdir(module_name):
                module = {"path": module_name, "ref": ref}
            else:
                module = findManifestEntry(manifest, module_name)

            if module:
                print(f"Updating {module_name}")
                if ref:
                    checkRevision(module, ref)
                else:
                    checkRevision(module)
            else:
                print(
                    f"""Cannot find manifest.json entry or user defined
component for {module_name}"""
                )

    else:
        for source in manifest["source-code"]:
            installModule(source)

        for third_party in manifest["third-party"]:
            installModule(third_party)

        for toolchain in manifest["toolchains"]:
            installModule(toolchain)

        sdk_base = os.getcwd()

        shutil.copytree(
            os.path.join(sdk_base, "boards"),
            os.path.join(sdk_base, "../boards"),
            dirs_exist_ok=True
        )

        shutil.copytree(
            os.path.join(sdk_base, "platforms"),
            os.path.join(sdk_base, "../platforms"),
            dirs_exist_ok=True
        )

        shutil.copyfile(
            os.path.join(sdk_base, "scripts/build.py"),
            os.path.join(sdk_base, "../build.py"),
        )
        shutil.copyfile(
            os.path.join(sdk_base, "scripts/kconfig/config.py"),
            os.path.join(sdk_base, "../config.py"),
        )
        shutil.copyfile(
            os.path.join(sdk_base, "CMakeLists.txt"),
            os.path.join(sdk_base, "../CMakeLists.txt"),
        )
        shutil.copyfile(
            os.path.join(sdk_base, "CMakePresets.json"),
            os.path.join(sdk_base, "../CMakePresets.json"),
        )
        shutil.copyfile(
            os.path.join(sdk_base, "platforms/CMakePresets.json"),
            os.path.join(sdk_base, "../platforms/CMakePresets.json"),
        )
        shutil.copyfile(
            os.path.join(sdk_base, "Kconfig"), os.path.join(sdk_base, "../Kconfig")
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-u",
        "--update",
        nargs="*",
        help="""Update components
of the SDK by passing their manifest.json entry name. Passing just the name will
pull in upstream updates. Passing the name followed by an @ symbol and a
commit hash, tag, or branch name will checkout that particular revision.""",
    )

    args = parser.parse_args()
    main(args)
