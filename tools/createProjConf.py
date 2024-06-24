import argparse
import json

def initProjConf(app_dir, jsonConfig):
    config = json.loads(jsonConfig)

    with open(f"{app_dir}/proj.conf", "w") as f:
        for key in config:
            val = config[key]
            if val == None or key.startswith("MENU_"):
                continue

            if val == True:
                val = "y"
            elif val == False:
                val = "n"
            elif type(val) == int:
                pass
            elif type(val) == str:
                val = f"\"{val}\""
            else:
                print(key, val, type(val))

            f.write(f"CONFIG_{key}={val}\n")
    return

def main(args):
    initProjConf(args.app_dir, args.config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a", "--app-dir", type=str, default="", help="directory for the new project"
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="json",
        help="proj.conf configuration settings",
    )

    args = parser.parse_args()
    main(args)