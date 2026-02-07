Do you forget the Makefile syntax whenever it's time to write one? I do. 

makemake crawls through directories in a c project to find all file dependencies and generates a makefile. It sets any file with an int main function as a target and crawls through the #include statements of the files to find dependencies. It catches dependencies included both in header and source files but it does so by assuming that header files have the same name as their corresponding source files. 

## User guide
1. Clone project.
2. Run "pip install -e . "
3. run "makemake" in the base directory of your c project. 

## Arguments
- -v --verbose: prints found dependencies and targets
- cf --compiler_flags: compiler flags passed during compilation
- -ldf --linker_flags: flags used during linking
- -cc --compiler: set the compiler
- -bd --binary_directory: destination for resulting binaries

## Limitations
Assumes header files share the name of their corresponding .c files. Only makes executables, edit Makefile manually for libraries. 
