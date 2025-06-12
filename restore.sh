#!/bin/bash

# Load environment variables
source config.env

# Activate virtualenv if needed
# source venv/bin/activate

# Call Python restore script with all arguments passed to this script
python restore.py "$@"