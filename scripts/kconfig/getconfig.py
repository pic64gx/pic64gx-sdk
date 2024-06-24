from kconfiglib import *
import os
import sys
import argparse
import json
from enum import Enum
import inspect
import time

sys.path.append(f"modules/kconfiglib")


symbolLookUp = {
    27: "int",
    3: "bool/tristate",
    47: "string",
    24: "hex",
    0: "n/a",
    31: "menu",
    100: "choice",
}

dependancyLookUp = {2: "AND", 39: "OR"}


def itemLookUp(item):
    if isChoice(item):
        return symbolLookUp[100]
    else:
        if type(item) == int:
            return symbolLookUp[item]
        else:
            return symbolLookUp[item.type]


def isChoice(item):
    if not type(item) == int:
        if hasattr(item, "syms"):
            return True
    return False


def getNodePath(node, path, syms):
    try:
        symbol = node.item.name
    except:
        try:
            all_caps_name = node.prompt[0].upper()
            underscore_name = all_caps_name.replace(" ", "_")
            symbol = f"MENU_{underscore_name}"

        except:
            symbol = None

    type = itemLookUp(node.item)

    path.append({"name": node.prompt[0], "type": type, "symbol": symbol})

    if node.parent == None:
        return path
    else:
        getNodePath(node.parent, path, syms)

    return path


def addPathToTree(tree, path, index_of_end_node):
    path_len = len(path)
    current = tree
    for i, node in enumerate(path):
        name = node["name"]
        node_type = node["type"]
        if "children" not in current:
            current["children"] = {}
        if name not in current["children"]:
            current["children"][name] = {"type": node_type, "symbol": node["symbol"]}

        # end of path
        if i == path_len - 1:
            current["children"][name]["index"] = index_of_end_node
        current = current["children"][name]


def detuple(tuple_list):
    arr = []
    for t in tuple_list:
        if type(t) == int:
            continue

        if type(t) == tuple:
            arr = arr + (detuple(list(t)))
        else:
            if dependancyLookUp[tuple_list[0]] == "AND":
                arr.append(t.name)
            else:
                arr.append([t.name])

    return arr


def getDependants(sym):
    _dependants = []
    dependants = []

    members = inspect.getmembers(sym)
    for m in members:
        if m[0] == "_dependents":
            _dependants = m[1]
            break

    for d in _dependants:
        dependants.append(d.name)

    return dependants


def getChoices(node):
    choices = []
    try:
        if isChoice(node.item):
            for c in node.item.syms:
                choices.append(c.name)
    except:
        pass
    return choices


def main(args):
    os.environ["srctree"] = args.workspace
    os.environ["KCONFIG_BINARY_DIR"] = args.build_dir
    os.environ["KCONFIG_APP_DIR"] = args.app_dir

    kconf = Kconfig(
        f"{args.workspace}/Kconfig",
        suppress_traceback=True,
        warn=False,
        warn_to_stderr=False,
    )

    if args.load == "":
        pass
    elif args.load == args.app_dir:
        kconf.load_config(f"{args.app_dir}/proj.conf")
    elif args.load == args.build_dir:
        kconf.load_config(f"{args.build_dir}/.config")

    unique_syms = kconf.unique_defined_syms
    syms = {}
    for s in unique_syms:
        syms[s.name] = s

    choices = kconf.choices
    menus = kconf.menus

    for c in choices:
        syms[c.name] = c

    menu = {}
    sym_data = {}

    for key in syms:
        sym = syms[key]
        sym_data[key] = None
        dependsOn = []
        node_choices = []
        dependants = getDependants(sym)
        help_string = ""
        """
        get symbol
        get the menu nodes for that symbol
        determine where each of those nodes are in the menu tree
        if the path to the node already exists in menu{} then insert it
        if not then create it
        if the node has been created because a child node appeared in the list
        of symbols then just fill in the necessary info
        """

        for i, n in enumerate(sym.nodes):
            help_string = sym.nodes[0].help
            path_to_node = list(reversed(getNodePath(n, [], syms)))
            addPathToTree(menu, path_to_node, i)

            if type(n.dep) == tuple:
                dep_list = detuple(list(n.dep))
                dependsOn.append(dep_list)
            else:
                if not n.dep.name == "y":
                    dependsOn.append([n.dep.name])
                else:
                    dependsOn.append([])

            node_choices = node_choices + getChoices(n)

        value = sym.str_value
        sym_type = itemLookUp(sym.type)

        if sym_type == "bool/tristate":
            if value == "y":
                value = True
            elif value == "n":
                value = False
            else:
                pass
        elif sym_type == "int":
            value = int(value)
        else:
            pass

        sym_data[key] = {
            "value": value,
            "dependsOn": dependsOn,
            "dependants": dependants,
            "choices": node_choices,
            "help": help_string
        }

    print(json.dumps({"menu": menu, "symbols": sym_data}))

    os.unsetenv("srctree")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="config",
        description="""""",
        epilog="",
    )

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
        "-d", "--build-dir", type=str, default="", help="Path to the build directory"
    )

    parser.add_argument(
        "-a",
        "--app-dir",
        type=str,
        default="",
        help="Path to the application directory",
    )

    parser.add_argument(
        "-l",
        "--load",
        type=str,
        default="",
        help="Path to the directory to load the config from",
    )

    # parser.add_argument(
    #     "-f",
    #     "--file_name",
    #     type=str,
    #     default=f"{sdk_base}/kconfig.json",
    #     help="File name/path for structured kconfig menu file",
    # )

    args = parser.parse_args()

    main(args)
