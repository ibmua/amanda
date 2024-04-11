"""
Usage
python3 combine_jsons.py --input outputs/response-of-the-file-filter
"""
import os
import json
import argparse

def combine_json_files(file_general_path):
    combined_data = {}

    # Iterate through the files with the specified pattern
    index = 0
    while True:
        file_path = f"{file_general_path}.{index}"
        if not os.path.exists(file_path):
            break

        # Read the JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
            combined_data.update(data)

        index += 1

    # Write the combined data to a new JSON file
    output_file = f"{file_general_path}_combined.json"
    with open(output_file, 'w') as file:
        json.dump(combined_data, file, indent=2)

    print(f"Combined JSON data saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine JSON files by merging top-level keys.")
    parser.add_argument("--input", required=True, help="The general path of the JSON files to combine.")
    args = parser.parse_args()

    combine_json_files(args.input)