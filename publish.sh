#!/bin/sh

set -e

# Install dependencies (SetupTools and Twine)
pip3 install --user -r ./requirements.txt

# Build the package
python3 ./setup.py sdist bdist_wheel

# Upload the package to PyPI
python3 -m twine upload ./dist/*

# Clean up temporary build directories
rm -rfv ./dist ./build
