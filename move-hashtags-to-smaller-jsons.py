"""
Usage
python3 move-hashtags-to-smaller-jsons.py --input hashtags/hashtags-sonnet.json --output hashtags/feed-to-ai.json --output-nocode hashtags/feed-to-ai-nocode.json
"""
import json
import argparse
import math


items_per_file = 25


def process_json(input_file, output_file, include_code):
    with open(input_file, 'r') as file:
        data = json.load(file)

    processed_data = {}
    for key, value in data.items():
        if value['file'][-3:] == ".rs" and include_code==0:
            continue

        processed_data[key] = value['tags']

        if isinstance(value['tags'], list):
            if value['file'][-3:] == ".rs":
                processed_data[key] = ["SourceCode"] + processed_data[key]
            if value['file'][-3:] == ".md" or value['file'][-4:] == ".mdx":
                if include_code:
                    processed_data[key] = ["Documentation"] + processed_data[key]
                else:
                    processed_data[key] = processed_data[key]

    num_items = len(processed_data)
    num_files = math.ceil(num_items / items_per_file)

    for i in range(num_files):
        start_index = i * items_per_file
        end_index = min((i + 1) * items_per_file, num_items)
        file_data = dict(list(processed_data.items())[start_index:end_index])

        output_file_name = f"{output_file}.{i}"
        with open(output_file_name, 'w') as output:
            json.dump(file_data, output, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Process JSON file')
    parser.add_argument('--input', type=str, required=True, help='Path to the input JSON file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output JSON file')
    parser.add_argument('--output-nocode', type=str, required=True, help='Path to the output JSON file for nocode version')
    args = parser.parse_args()

    process_json(args.input, args.output, 1)
    process_json(args.input, args.output_nocode, 0)

if __name__ == '__main__':
    main()