#!/bin/bash

# Get the current date and time for the backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Set the path to the JSON file you want to backup
JSON_FILE="CTVM_bot/data/restaurants_db.json"

# Create the backup filename with timestamp
BACKUP_FILE="CTVM_bot/data/restaurants_db_${TIMESTAMP}.json"

# Check if the source file exists
if [ -f "$JSON_FILE" ]; then
    # Make a copy of the file
    cp "$JSON_FILE" "$BACKUP_FILE"
    echo "Backup created: $BACKUP_FILE"
else
    echo "Error: Source file $JSON_FILE does not exist."
    exit 1
fi