#!/bin/sh

set -e

# Make sure the output directory is empty
rm -rfv ./dist/*

# Install dependencies (SetupTools and Twine)
pip3 install --upgrade --user -r ./requirements.txt

# Build the package
python3 ./setup.py sdist bdist_wheel

# Upload the package to PyPI
python3 -m twine upload ./dist/*
