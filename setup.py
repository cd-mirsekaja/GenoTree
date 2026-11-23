from setuptools import setup, find_packages

from src.genotree.const import PROJECT_VERSION

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name = "genotree",
    version = PROJECT_VERSION,
    description = "Perform a detailed phylogenetic analysis on a combined dataset of genomes and genes",
    author = "Ronja Rösner",
    author_email = "ronja.roesner@uni-oldenburg.de",
    package_dir = {"": "src"},
    packages = find_packages(include = ['genotree', 'genotree.*', 'types', 'types.*']),
    include_package_data = True,
    install_requires = requirements,
    entry_points = {
        "console_scripts": ["genotree=genotree.cli.entry:main"]
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Unix Shell",
        "Operating System :: OS Independent",
    ],
    python_requires = ">=3.10",
)