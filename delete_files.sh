#!/bin/bash

folder="/path/to/folder"
log_file="/path/to/logs/delete_$(date +%Y-%m-%d).log"

for file in "$folder"/*; do
    [ -f "$file" ] || continue

    if lsof "$file" > /dev/null 2>&1; then
        echo "$(date '+%F %T') - Skipped (in use): $file" >> "$log_file"
    else
        echo "$(date '+%F %T') - Deleting: $file" >> "$log_file"
        rm -f "$file"
    fi
done
