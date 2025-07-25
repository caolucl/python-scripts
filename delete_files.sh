#!/bin/bash

folder="/path/to/folder"

for file in "$folder"/*; do
    # Skip if not a regular file
    [ -f "$file" ] || continue

    # Check if file is in use
    if lsof "$file" > /dev/null 2>&1; then
        echo "Skipping (in use): $file"
    else
        echo "Deleting: $file"
        rm -f "$file"
    fi
done
