#!/bin/bash

echo "Migration started!"

# Directory to search for .py files; default is current directory
DIR="${1:-.}"

# Find all .py files in the directory (non-recursive)
for file in "$DIR"/*.py; do
  # Check if any .py files were found
  [ -e "$file" ] || continue

  echo "Running: $file"
  python "$file"

  # Check exit status
  if [ $? -ne 0 ]; then
    echo "Error: $file failed to run."
    exit 1
  fi
done

echo "Migration done!"
exit 0