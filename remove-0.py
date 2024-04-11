"""
Usage
python3 remove-0.py  --json-selection "outputs/response-of-the-file-filter_combined.json"  >  outputs/response-of-the-file-filter_non-zero.json
"""
import json
import argparse

def remove_zero_value_keys(json_data):
    filtered_data = {key: value for key, value in json_data.items() if value != 0}
    return filtered_data

def process_json_file(json_selection_path):
    # Load the JSON file
    with open(json_selection_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Remove keys with value 0
    filtered_data = remove_zero_value_keys(json_data)

    return filtered_data

# Parse command line arguments
parser = argparse.ArgumentParser(description='Remove keys with value 0 from a JSON file.')
parser.add_argument('--json-selection', dest='json_selection_path', required=True,
                    help='Path to the JSON selection file')

args = parser.parse_args()

# Process the JSON file and get the filtered data
result = process_json_file(args.json_selection_path)

# Print the filtered data as JSON
print(json.dumps(result, indent=2))