#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== 1. Cleaning up previous builds ==="
rm -rf dist build *.egg-info
rm -rf venv_test

echo "=== 2. Building the package ==="
python3 -m build

echo "=== 3. Creating a temporary virtual environment ==="
python3 -m venv venv_test
source venv_test/bin/activate

echo "=== 4. Installing the package from the built wheel ==="
# Find the .whl file in dist/ and install it with extra dependencies
WHEEL_FILE=$(ls dist/*.whl)
pip install "$WHEEL_FILE[visualizer,fabricator]"

echo "=== 5. Verifying imports ==="
python3 -c "
import openrocket_parser
print('Successfully imported openrocket_parser')
from openrocket_parser.simulations.loader import load_simulations_from_xml
print('Successfully imported load_simulations_from_xml')
"

echo "=== 6. Verifying CLI tools ==="
if command -v openrocket-visualizer >/dev/null 2>&1; then
    echo "openrocket-visualizer is installed."
else
    echo "ERROR: openrocket-visualizer NOT found."
    exit 1
fi

if command -v openrocket-fabricator >/dev/null 2>&1; then
    echo "openrocket-fabricator is installed."
else
    echo "ERROR: openrocket-fabricator NOT found."
    exit 1
fi

echo "=== SUCCESS: The package seems to be working correctly! ==="
echo "You can now manually test the tools inside the venv if needed:"
echo "source venv_test/bin/activate"
