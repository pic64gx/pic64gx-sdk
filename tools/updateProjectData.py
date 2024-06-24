import argparse
import tokenize as tkz
import re
import os
import pathlib

def main(args):
    directory = pathlib.Path(os.path.abspath(args.directory)).as_posix()
    sourcesString = 'target_sources(${PROJECT_NAME} PUBLIC\n'

    for src in args.source_files:
        src = src.replace(directory, "${CMAKE_CURRENT_SOURCE_DIR}")
        sourcesString += f'\t{src}\n'

    sourcesString += ')'

    includeDirsString = 'target_include_directories(${PROJECT_NAME} PUBLIC\n'

    for inc in args.include_directories:
        inc = inc.replace(directory, "${CMAKE_CURRENT_SOURCE_DIR}")
        includeDirsString += f'\t{inc}\n'

    includeDirsString += ')'

    with open(f"{directory}/CMakeLists.txt", 'r') as f:
        file = f.read()

        file = re.sub(r'target_sources\([\S\s]+?\)', sourcesString, file)

        file = re.sub(r'target_include_directories\([\S\s]+?\)', includeDirsString, file)

    with open(f"{directory}/CMakeLists.txt", 'w') as f:
        f.write(file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--directory", type=str, default="", help="project directory"
    )

    parser.add_argument("-s", "--source-files", nargs="*")

    parser.add_argument("-i", "--include-directories", nargs="*")

    args = parser.parse_args()

    main(args)