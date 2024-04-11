"""
Usage
python3 cli-add-ids.py  --input help/help-descriptions-only.json  --output help/help-descriptions-and-ids.json

    -- produces files like help/help-descriptions-and-ids.json.0, help/help-descriptions-and-ids.json.1, help/help-descriptions-and-ids.json.2 ..
    due to max_items_per_file
"""

import json
import argparse
import math

# Create an argument parser
parser = argparse.ArgumentParser(description='Convert JSON format')
parser.add_argument('--input', type=str, help='Path to the input JSON file', required=True)
parser.add_argument('--output', type=str, help='Path to the output JSON file', required=True)

# Parse the command-line arguments
args = parser.parse_args()

# Load the JSON data from the input file
with open(args.input) as file:
    data = json.load(file)

# Create a new dictionary to store the converted data
converted_data = {}

# Iterate over the key-value pairs in the original data
for index, (key, value) in enumerate(data.items(), start=1):
    # Convert the index to a string and create a list with the key and value
    converted_data[str(index)] = [key, value]

# Calculate the number of files needed
max_items_per_file = 250
num_files = math.ceil(len(converted_data) / max_items_per_file)

# Split the converted data into multiple files
for i in range(num_files):
    start_index = i * max_items_per_file
    end_index = min((i + 1) * max_items_per_file, len(converted_data))
    
    # Create a subset of the converted data for the current file
    file_data = {k: v for k, v in list(converted_data.items())[start_index:end_index]}
    
    # Generate the output file name with the file number
    output_file = f"{args.output}.{i}"
    
    # Save the file data to the output file
    with open(output_file, 'w') as file:
        json.dump(file_data, file, indent=0)