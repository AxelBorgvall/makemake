makemake crawls through directories in a c project to find all file dependencies and generates a makefile. 

## Arguments
- -v --verbose: prints found dependencies and targets
- cf --compiler_flags: compiler flags passed during compilation
- -ldf --linker_flags: flags used during linking
- -cc --compiler: set the compiler
- -bd --binary_directory: destination for resulting binaries

## Limitations
Assumes header files share the name of their corresponding .c files. Only makes executables, edit Makefile manually for libraries. 
