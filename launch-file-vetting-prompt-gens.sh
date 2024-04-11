#!/bin/bash

FILENAME="hashtags/feed-to-ai.json"

i=0

while true; do
    if [ "$1" = "nocode" ]; then
        if [ -f "hashtags/feed-to-ai-nocode.json.${i}" ]; then
            python3 parse-template.py --template templates/file-filter-request.template --question outputs/question --hashtags "hashtags/feed-to-ai-nocode.json.${i}" --output "outputs/file-filter.prompt.${i}"
            # echo $i
            i=$((i + 1))
        else
            break
        fi
    else
        if [ -f "${FILENAME}.${i}" ]; then
            python3 parse-template.py --template templates/file-filter-request.template --question outputs/question --hashtags "hashtags/feed-to-ai.json.${i}" --output "outputs/file-filter.prompt.${i}"
            # echo $i
            i=$((i + 1))
        else
            break
        fi
    fi
done

# echo "$1"