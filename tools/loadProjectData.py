import argparse
import tokenize as tkz
import json

def filterArr(arr):
    return list(filter(lambda x : x != '\\' and x != 'PUBLIC' and x != '(' and x != '(${PROJECT_NAME}', arr))


def main(args):
    bracketIndex = 0

    target_sources = []
    collectingSources = False
    sourcesBracketIndex = 0

    target_include_directories = []
    collectingIncludes = False
    includesBracketIndex = 0

    with tkz.open(f"{args.directory}/CMakeLists.txt") as f:
        tokens = tkz.generate_tokens(f.readline)

        for t in tokens:
            if t.exact_type == tkz.LPAR:
                bracketIndex += 1

            if t.exact_type == tkz.RPAR:
                bracketIndex -= 1

            if t.string == "target_sources":
                collectingSources = True
                sourcesBraketIndex = bracketIndex
                continue

            if collectingSources:
                if not bracketIndex == sourcesBracketIndex:
                    if (not t.exact_type == tkz.ERRORTOKEN) or t.string == '$':
                        target_sources.append(t)
                else:
                    collectingSources = False

            if t.string == "target_include_directories":
                collectingIncludes = True
                includesBracketIndex = bracketIndex
                continue

            if collectingIncludes:
                if not bracketIndex == includesBracketIndex:
                    if (not t.exact_type == tkz.ERRORTOKEN) or t.string == '$':
                        target_include_directories.append(t)
                else:
                    collectingIncludes = False

    src = tkz.untokenize(target_sources)
    src = src.split()
    src = filterArr(src)


    inc = tkz.untokenize(target_include_directories)
    inc = inc.split()
    inc = filterArr(inc)

    print(json.dumps({
        'src': src,
        'inc': inc
    }))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--directory", type=str, default="", help="project directory"
    )

    args = parser.parse_args()
    main(args)
