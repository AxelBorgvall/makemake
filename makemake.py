from jinja2 import Environment, FileSystemLoader
import pathlib
from collections import defaultdict
import re
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog='makemake',
        description='Automated Makefile generator for C projects'
    )

    parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='Print the crawl logic and found dependencies')

    parser.add_argument('-cf', '--compiler-flags', 
                        type=str,
                        default='-Wall -Wextra -Iinclude -O2',
                        help='Compiler flags to be passed during compilation')

    parser.add_argument('-ldf', '--linker-flags', 
                        type=str,
                        default='',
                        help='Linker flags to be used during linking')
    
    parser.add_argument('-cc', '--compiler', 
                        type=str,
                        default='gcc',
                        help='Compiler to be called')
    
    parser.add_argument('-c','--comments',
                        action='store_true',
                        help='Wether to add cheatsheet like comments to the makefile')

    # parser.add_argument('-n', '--num_things', 
    #                     type=int,
    #                     default=1,
    #                     help='An example numerical parameter (e.g., 20)')

    args = parser.parse_args()

    
    # Crawl for dependencies and targets
    targets=[]
    dependencies=defaultdict(set)
    scan_dir(pathlib.Path.cwd(),targets,dependencies)
    if args.verbose:
        print("File dependencies")
        print_dep(dependencies)
        print("Target binaries")
        print([t.name for t in targets])
    
    # Look for build
    build_exists=False
    for x in pathlib.Path.cwd().iterdir():
        if x.is_dir() and x.name.lower() == "build":
            build_exists=True
            build_name=x.name

    # Boolean to make build if not present
    if not build_exists:
        build_name="build"
        pathlib.Path.cwd()/ pathlib.Path(build_name)

    # List all files to compile
    objects=set()
    for t in targets:
        for d in dependencies[t.stem]:
            objects.add(d)
    if args.verbose:
        print("Object files to compile: ",*[o.stem for o in objects])

    # Write the makefile


# Checks listed dependencies in one file
def get_dependencies(path,dependencies):
    s=path.read_text(encoding="utf-8")
    includes = re.findall(r'#include\s+"([^"]+)"', s)
    dependencies[path.stem]=set.union(
        set([path/dep for dep in includes]),
        dependencies[path.stem]
    ) 
    return 

# Checks is a file should be the source for a binary
def check_target(path):
    s = path.read_text(encoding="utf-8")
    s = re.sub(r"//.*", "", s)
    return bool(re.search(r"^\s*int\s+main\s*\(", s, re.MULTILINE))

# Searches through directory for potential targets and executables
def scan_dir(path,targets,dependencies):
    for x in path.iterdir():
        if x.is_file():
            if x.suffix==".c" or x.suffix==".h":
                if check_target(x):
                    targets.append(x)
                get_dependencies(x,dependencies)
        elif x.is_dir():
            scan_dir(x,targets,dependencies)

def print_dep(d):
    print("{")
    for key,value in d.items():
        print("\t[",key,"]: ",*[path.stem for path in value])
    print("}")        



if __name__ == "__main__":
    main()

