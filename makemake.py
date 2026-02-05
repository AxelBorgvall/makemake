from jinja2 import Environment, FileSystemLoader
import pathlib
from collections import defaultdict
import re
import argparse
import sys

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
    templates=make_templates(templates_path)

    makestring=""

    # Define directories
    makestring+=templates['def'].render(varname="BUILD_DIR",data=build_name)+"\n"
    makestring+=templates['def'].render(varname="BIN_DIR",data=args.binary_directory)+"\n\n"
    # Compiler and flags
    makestring+=templates['flags'].render(compiler=args.compiler,cflags=args.compiler_flags,ldflags=args.linker_flags)+"\n\n"
    # Define each target
    target_strings=" ".join(t.stem for t in targets )
    makestring+=templates['def'].render(varname="TARGETS",data=target_strings)+"\n\n"
    makestring+="all:$(TARGETS)\n\n"
    #Write make rules
    makestring+=write_rules(targets,file_dependencies,c_files,templates,args,build_name)

    makestring+="-include $(wildcard build/*.d)\n\n"
    makestring+=templates['clean'].render()
    fpath=pathlib.Path("Makefile")
    fpath.write_text(makestring)

def make_templates(templates_path):
    env = Environment(loader=FileSystemLoader(templates_path))
    def replace_list(strings):
        return [s.replace('.o','.d') for s in strings]
    env.filters['replace']=replace_list
    templates={}
    templates['def']= env.get_template('def.j2')
    templates['flags']=env.get_template('compilerflags.j2')
    templates['compile']=env.get_template('compile.j2')
    templates['link']=env.get_template('link.j2')
    templates['clean']=env.get_template('clean.j2')
    return templates


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
    
    parser.add_argument('-bd','--binary_directory',
                        type=str,
                        default='.',
                        help='Directory to put resulting binaries inside'
                        )

    return parser.parse_args()

def write_rules(targets,file_dependencies,c_files,templates,args,build_name):
    rules_string=""
    compiled_dependencies=[]

    for t in targets:
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

        # Compile all needed object files
        for src in sources:
            if src not in compiled_dependencies:
                rules_string+=templates['compile'].render(
                    obj_path=build_name+"/"+src.stem+".o",
                    src_path=str(src.relative_to(pathlib.Path.cwd()).as_posix())
                )+"\n\n"
                compiled_dependencies.append(src)
        
        # Link into an executable
        rules_string+=templates['link'].render(
            all_objs=["\\\n\t"+str(src.relative_to(pathlib.Path.cwd()).as_posix()).replace('.c','.o') for src in sources],
            bin_path=args.binary_directory+"/"+t.stem
        )+"\n\n"
    return rules_string

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
