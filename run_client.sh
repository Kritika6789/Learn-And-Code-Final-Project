#!/bin/bash
# run_client.sh

# Change to the directory of the script
cd "$(dirname "$0")"

# Activate the virtual environment if it exists
if [ -d "server/venv" ]; then
    source server/venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set the python path so imports work correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the client application
python client/app.py
