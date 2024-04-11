"""
Joining and outputting the most important files provided their priority.

Usage
python3 all-docs-joined.py  --json-selection outputs/refined-file-priorities.json  --json-all-hashtags "hashtags/hashtags-sonnet.json"  >  outputs/joined-selected-files
"""

import json
import argparse

max_context = 400000

def process_json_files(json_selection_path, json_all_hashtags_path):
    result_string = ""
    doc_id = 1

    # Load JSON files
    with open(json_selection_path, 'r') as json_selection_file:
        json_selection = json.load(json_selection_file)

    with open(json_all_hashtags_path, 'r') as json_all_hashtags_file:
        json_all_hashtags = json.load(json_all_hashtags_file)

    # Iterate over the values from 10 to 1
    for value in range(10, 0, -1):
        # Iterate over the JSON selection
        for key, entry_value in json_selection.items():
            if entry_value == value:
                # Retrieve the corresponding entry from json_all_hashtags
                if key in json_all_hashtags:
                    entry = json_all_hashtags[key]
                    content = entry["content"]
                    file_name = entry["file"]

                    # Add the content and file name to the result string
                    result_string += f"<document index=\"{doc_id}\">\n<source>{file_name}</source>\n<document_content>\n{content}\n</document_content></document>\n\n"
                    doc_id += 1

                    # Check if the length of the result string exceeds max_context characters
                    if len(result_string) > max_context:
                        return result_string

    return result_string

# Parse command line arguments
parser = argparse.ArgumentParser(description='Build a string from JSON files.')
parser.add_argument('--json-selection', dest='json_selection_path', required=True,
                    help='Path to the JSON selection file')
parser.add_argument('--json-all-hashtags', dest='json_all_hashtags_path', required=True,
                    help='Path to the JSON all hashtags file (including directory)')
args = parser.parse_args()

# Process the JSON files and get the result string
result = process_json_files(args.json_selection_path, args.json_all_hashtags_path)

# Print the result string
print("<documents>")
print(result)
print("</documents>")