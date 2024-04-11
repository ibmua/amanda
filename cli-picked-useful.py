"""
Usage
python3 cli-picked-useful.py --cli-response-json outputs/about-cli-response.json --cli-desc-and-ids-json help/help-descriptions-and-ids.json --full-cli-json help/namada-help.json
"""

import json
import argparse

def generate_output(cli_response_json, cli_desc_and_ids_json, full_cli_json):
    output = ""

    for id, value in cli_response_json.items():
        if value > 1:
            cli_command = cli_desc_and_ids_json[id][0]
            if cli_command in full_cli_json:
                help_text = full_cli_json[cli_command]
                output += f"<cli>{cli_command} --help\n\n{help_text}\n</cli>\n\n"

    return output

def main():
    parser = argparse.ArgumentParser(description="Generate output based on JSON files.")
    parser.add_argument("--cli-response-json", type=str, required=True, help="Path to the CLI response JSON file.")
    parser.add_argument("--cli-desc-and-ids-json", type=str, required=True, help="Path to the CLI description and IDs JSON file.")
    parser.add_argument("--full-cli-json", type=str, required=True, help="Path to the full CLI JSON file.")

    args = parser.parse_args()

    with open(args.cli_response_json, "r") as f:
        cli_response_json = json.load(f)

    with open(args.cli_desc_and_ids_json, "r") as f:
        cli_desc_and_ids_json = json.load(f)

    with open(args.full_cli_json, "r") as f:
        full_cli_json = json.load(f)

    output = generate_output(cli_response_json, cli_desc_and_ids_json, full_cli_json)
    print(output)

if __name__ == "__main__":
    main()