#!/bin/bash

# Define the path to the script
SCRIPT_PATH="/home/myisp/Documents/GitHub/G915ColorC/change_color.py"

# Check if the script exists
if [ -f "$SCRIPT_PATH" ]; then
    # Run the Python script
    python3 "$SCRIPT_PATH"
else
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

