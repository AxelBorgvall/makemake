from jinja2 import Environment, FileSystemLoader
import pathlib
from collections import defaultdict
import re
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        prog='makemake',
        description='Automated Makefile generator for C projects'
    )

    parser.add_argument('-v', '--verbose', 
                        action='store_true', 
                        help='Print the crawl logic and found dependencies')

    parser.add_argument('-cf', '--compiler_flags', 
                        type=str,
                        default='-Wall -Wextra -Iinclude -O2',
                        help='Compiler flags to be passed during compilation')

    parser.add_argument('-ldf', '--linker_flags', 
                        type=str,
                        default='',
                        help='Linker flags to be used during linking')
    
    parser.add_argument('-cc', '--compiler', 
                        type=str,
                        default='gcc',
                        help='Compiler to be called')
    
    # parser.add_argument('-c','--comments',
    #                     action='store_true',
    #                     help='Wether to add cheatsheet like comments to the makefile')
    
    parser.add_argument('-bd','--binary_directory',
                        type=str,
                        default='.',
                        help='Directory to put resulting binaries inside'
                        )

    # parser.add_argument('-n', '--num_things', 
    #                     type=int,
    #                     default=1,
    #                     help='An example numerical parameter (e.g., 20)')

    return parser.parse_args()

def main():
    # Parse commandline args
    args=parse_args()
    
    # Crawl for dependencies and targets
    targets=[]
    file_dependencies=defaultdict(set)
    c_files={}
    scan_dir(pathlib.Path.cwd(),targets,file_dependencies,c_files)
    if args.verbose:
        print("File dependencies")
        print_dep(file_dependencies)
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
        for d in file_dependencies[t.stem]:
            objects.add(d)
    if args.verbose:
        print("Object files to compile: ",*[o.stem for o in objects])
    
        
    
    # Create string for makefile ----------------------------------------------------------
    # Loading templates
    templates_path = pathlib.Path(__file__).parent.resolve()/"templates"   
    env = Environment(loader=FileSystemLoader(templates_path))
    definition_template = env.get_template('def.j2')
    compiler_template=env.get_template('compiler.j2')
    builder_template=env.get_template('recipe.j2')
    makestring=""

    # Define directories
    makestring+=definition_template.render(varname="BUILD_DIR",data=build_name)+"\n"
    makestring+=definition_template.render(varname="BIN_DIR",data=args.binary_directory)+"\n\n"
    # Compiler and flags
    makestring+=compiler_template.render(compiler=args.compiler,cflags=args.compiler_flags,ldflags=args.linker_flags)+"\n\n"
    # Define each target
    target_strings=" ".join(t.stem for t in targets )
    makestring+=definition_template.render(varname="TARGETS",data=target_strings)+"\n\n"
    # Define sources for each target
    # List all targets
    for t in targets:
        makestring+=t.stem+"_SOURCES:="
        sources=set()
        sources.add(t)
        
        queue = [t]
        processed_stems = {t.stem}
        while queue:
            curr = queue.pop(0)
            for dep in file_dependencies[curr.stem]:
                if dep.stem in c_files and dep.stem not in processed_stems:
                    processed_stems.add(dep.stem)
                    c_file = c_files[dep.stem]
                    sources.add(c_file)
                    queue.append(c_file)

        makestring+=" ".join(str(s.relative_to(pathlib.Path.cwd()).as_posix()) for s in sources)
        makestring+="\n"
    makestring+="\n"
    # Make all target binaries
    makestring+="all: $(TARGETS)\n\n"
    # This adds a function for dynamically compiling and linking and calls it once for every target
    # Also adds a clean function
    makestring+=builder_template.render()

    fpath=pathlib.Path("Makefile")
    fpath.write_text(makestring)

# Checks listed dependencies in one file
def get_dependencies(path,dependencies):
    s=path.read_text(encoding="utf-8")
    includes = re.findall(r'#include\s+"([^"]+)"', s)
    dependencies[path.stem]=set.union(
        set([(path.parent / dep).resolve() for dep in includes]),
        dependencies[path.stem]
    ) 
    return 

# Checks is a file should be the source for a binary
def check_target(path):
    s = path.read_text(encoding="utf-8")
    s = re.sub(r"//.*", "", s)
    return bool(re.search(r"^\s*int\s+main\s*\(", s, re.MULTILINE))

# Searches through directory for potential targets and executables
def scan_dir(path,targets,dependencies,c_files):
    for x in path.iterdir():
        if x.is_file():
            if x.suffix==".c":
                c_files[x.stem]=x
            if x.suffix==".c" or x.suffix==".h":
                if check_target(x):
                    targets.append(x)
                get_dependencies(x,dependencies)
        elif x.is_dir():
            scan_dir(x,targets,dependencies,c_files)

def print_dep(d):
    print("{")
    for key,value in d.items():
        print("\t[",key,"]: ",*[path.stem for path in value])
    print("}")        



if __name__ == "__main__":
    main()
