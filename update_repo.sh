#!/bin/bash

# Check if a URLs file argument is provided
if [ -z "$1" ]; then
    echo "Error: No URLs file provided. Please provide the path to the URLs file."
    exit 1
fi

URLS_FILE="$1"

# Remote branch
REMOTE_BRANCH="master"

# Check if the URLs file exists
if [ ! -f "$URLS_FILE" ]; then
    echo "Error: URLs file not found: $URLS_FILE"
    exit 1
fi

# Loop through each URL in the file and run git subtree command
while IFS= read -r url; do
    # Extract the last part of the URL to use as the local directory name
    local_dir=$(basename "$url" .git)

    echo "Processing subtree for URL: $url"

    # Check if the directory already exists
    if [ -d "$local_dir" ]; then
        echo "Directory $local_dir already exists. Updating subtree..."
        git subtree pull --prefix "$local_dir" "$url" "$REMOTE_BRANCH" --squash
        if [ $? -ne 0 ]; then
            echo "Error: Failed to update subtree for URL: $url"
        else
            echo "Subtree updated successfully for URL: $url"
        fi
    else
        echo "Adding new subtree..."
        git subtree add --prefix "$local_dir" "$url" "$REMOTE_BRANCH" --squash
        if [ $? -ne 0 ]; then
            echo "Error: Failed to add subtree for URL: $url"
        else
            echo "Subtree added successfully for URL: $url"
        fi
    fi
done < "$URLS_FILE"

# Push the changes
git push

echo "All subtrees updated successfully"
