

Give the user (or yourself) options via command-line arguments:


To make it look great on GitHub, organize the repository like this:
autobuild.py: The core engine.
templates/: Folder containing jinja2 or basic text templates for the Makefile or CMakeLists.txt.
test_project/: A dummy C++ project so people can clone it and run python autobuild.py immediately to see the magic happen.
README.md: A clean explanation with a GIF of the script running.

If A.c includes B.h and C.h, and both B.h and C.h include D.h, make sure your script doesn't lose its mind or try to compile D.c twice.

# setup
Create a file called setup.py (or pyproject.toml) in project root:
Python

from setuptools import setup
```
setup(
    name='makemake',
    version='0.1.0',
    py_modules=['makemake'],
    entry_points={
        'console_scripts': [
            'makemake = makemake:main', # Calls the main() function in makemake.py
        ],
    },
)
```
You run pip install -e . in your project folder.

Python creates a wrapper called makemake in your Python's /Scripts or /bin folder (which is already in your PATH).

Now, you can just type makemake in any folder, and it runs.
# arguments
Make it so that different types can be set for different targets in one makefile. Default binary, if in include/lib make it a library. 
--v # verbose
--type=library: Generates a static/dynamic library build.
--type=executable: Generates a standard binary.
--standard=c++20: Sets the compiler flags automatically.
--c # memory comments in the resulting makefile

# multiple targets
Crawl everything: Find every file that contains int main().
Define Targets: For each "main" file found, create a build rule named after that file.
The "All" Rule: At the top of the Makefile, create an all target that builds everything.
What the user experience looks like:
- User types make: Builds everything.
- User types make server: Builds only the server.
- User types make tests: Builds only the tests.


Search outward for the dependencies of each and only link necessary. 

# verbose demo
Step 1: User types makemake.
Step 2: Script prints:
🔍 Searching for entry points...
🎯 Found: ./src/main.c (Target: app)
🎯 Found: ./tests/test_suite.c (Target: tests)
🕸️ Crawling dependencies for 'app'...
-> Found player.c, physics.c, utils.c
✅ Generated Makefile with 2 targets.
Step 3: User types ls to show the new Makefile.

# limitations
- Assumes corresponding .h and .c files share the same name