#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

# Create venv if needed

if [ ! -d "$VENV_DIR" ]; then
    python3.13 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python3.13 -m pip install --upgrade pip
python3.13 -m pip install --upgrade build twine

python3.13 -m build
python3.13 -m twine check dist/*

python3.13 -m zipfile -l dist/*.whl

read -r -p "Upload to PyPI? [y/N] " answer

if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
    echo "Upload cancelled."
    exit 0
fi

python3.13 -m twine upload dist/*