#!/usr/bin/env bash

# Define the directory path
dir_path="$HOME/Projects/github/auto_doc"

# Check if the .env file exists in the local directory
env_file="$dir_path/.env"
if [[ ! -f "$env_file" ]]; then
    echo "Error: .env file not found in $dir_path"
    exit 1
fi

# Read the OPENAI_API_KEY variable from the .env file and export it
OPENAI_API_KEY=$(grep -E '^OPENAI_API_KEY=' "$env_file" | cut -d '=' -f2-)
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "Error: OPENAI_API_KEY variable not found in the .env file"
    exit 1
fi
export OPENAI_API_KEY

# Define the script path
script_path="$dir_path/main.py"

# Activate the virtual environment
source "$dir_path/.venv/bin/activate"

# Run the Python script
python3 "$script_path" "$@" 2>&1
