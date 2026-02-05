from setuptools import setup

setup(
    name='makemake',
    version='0.1.0',
    py_modules=['makemake'],
    install_requires=[
        'jinja2',
    ],
    entry_points={
        'console_scripts': [
            'makemake = makemake:main', # Calls the main() function in makemake.py
        ],
    },
)