#!/usr/bin/env python3
"""
AI-hashtag-generator.py

This script processes files in specified folders, reads their content, and generates hashtags based on the content using the Anthropic API (either directly or through Google Vertex). The generated hashtags and file information are then saved to a JSON output file. It can integrate with a previous output file to avoid reprocessing the same files.

Usage:
    python3 AI-hashtag-generator.py --folders FOLDER1 .EXT1,.EXT2 FOLDER2 .EXT3 FOLDER3 "*" --output OUTPUT_FILE [--ignore IGNORE_FILES] [--dont-integrate-old] [--truncate] [--model MODEL]
    python3 AI-hashtag-generator.py --folders ~/namada/namada-docs-master/ .mdx ~/namada/namada-main/ .mdx,.md,.rs  supplemental-materials/ "*"  --output hashtags/hashtags-sonnet.json --ignore CHANGELOG.md --model sonnet --truncate
    python3 AI-hashtag-generator.py --folders namada-src/ .mdx,.md,.rs  supplemental-materials/ "*"  --output hashtags/hashtags-sonnet.json --ignore CHANGELOG.md --model sonnet --truncate

Arguments:
    --folders       List of folders to process, followed by comma-separated file extensions for each folder. "*" for all files including those without an extension (without a dot in their name).
    --output        Output JSON file name
    --ignore        Comma-separated list of file names to ignore (optional)
    --model         Anthropic model to use: "sonnet", "opus", or "haiku" (default: "sonnet")
    --dont-integrate-old Should we update generate
    --truncate      Remove files from the JSON that are not listed in the selected folders (optional)

Environment Variables:
    CLAUDE_API_KEY  Anthropic API key
    GOOGLE_PROJECT_ID Google Cloud project ID (required when using the Google API)
    AMANDA_API      API to use: "anthropic" or "google" (default: "anthropic")


Note: The script requires the 'anthropic' library to be installed. For Google Vertex, additional setup is required.
"""

import os
import anthropic
import argparse
import ast
import subprocess
import json
import time
from termcolor import colored

# Create an argument parser
parser = argparse.ArgumentParser(description='Process files in specified folders.')
parser.add_argument('--folders', nargs='+', help='List of folders to process, followed by comma-separated file extensions for each folder')
parser.add_argument('--output', type=str, help='Output file name', required=True)
parser.add_argument('--ignore', type=str, help='Comma-separated list of file names to ignore', default='')
parser.add_argument('--model', type=str, help='Anthropic model to use: "sonnet", "opus", or "haiku" (default: "sonnet")', default='sonnet')
parser.add_argument('--dont-integrate-old', action='store_true', help="Don't use Old output JSON file to new hashtags with old ones")
parser.add_argument('--truncate', action='store_true', help='Remove files from the JSON that are not listed in the selected folders')
args = parser.parse_args()

# Get the Anthropic API key from the environment variable

# Get the API to use from the environment variable
api = os.environ.get('AMANDA_API', 'anthropic')

# Set up the Anthropic or Google Vertex client based on the AMANDA_API environment variable
if api == 'anthropic':
    api_key = os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        raise ValueError('CLAUDE_API_KEY environment variable is not set.')
    client = anthropic.Anthropic(api_key=api_key)
elif api == 'google':
    from anthropic import AnthropicVertex
    project_id = os.environ.get('GOOGLE_PROJECT_ID')
    if not project_id:
        raise ValueError('GOOGLE_PROJECT_ID environment variable is not set.')
    client = AnthropicVertex(region="us-central1", project_id=project_id)
else:
    raise ValueError(f"Invalid API: {api}. Choose 'anthropic' or 'google'.")

# Set the Anthropic model based on the --model argument
if api == 'anthropic':
    if args.model == 'sonnet':
        model = "claude-3-sonnet-20240229"
    elif args.model == 'opus':
        model = "claude-3-opus-20240229"
    elif args.model == 'haiku':
        model = "claude-3-haiku-20240307"
    else:
        raise ValueError(f"Invalid model: {args.model}. Choose 'sonnet', 'opus', or 'haiku'.")
else:  # Google API
    if args.model == 'sonnet':
        model = "claude-3-sonnet@20240229"
    elif args.model == 'opus':
        model = "claude-3-opus@20240229"
    elif args.model == 'haiku':
        model = "claude-3-haiku@20240307"
    else:
        raise ValueError(f"Invalid model: {args.model}. Choose 'sonnet', 'opus', or 'haiku'.")

hashtags_for_all = {}
processed_files = {}
all_files_currently = set()
total_usage = 0

# Load old output file if provided
if not args.dont_integrate_old:
    try:
        with open(args.output, 'r') as old_output_file:
            old_hashtags = json.load(old_output_file)

            for num, data in old_hashtags.items():
                file_path = data['file']
                if not os.path.exists(file_path):
                    raise ValueError(f"File path '{file_path}' from the old output does not exist.")
                processed_files[file_path] = num

            hashtags_for_all = old_hashtags
            print(f"Loaded {len(hashtags_for_all)} entries from the old output file.")
    except FileNotFoundError:
        print(f"No old output file '{args.output}' not found. Proceeding without integration.")

file_num = 0

# Check if folders are provided
if args.folders:
    # Iterate through each folder and its extensions
    for i in range(0, len(args.folders), 2):
        folder = args.folders[i]
        extensions = args.folders[i+1].split(',')
        
        # Generate the find command based on the extensions
        extensions_str = ' -o '.join([f"-name '*{ext}'" for ext in extensions])
        command = f"find {folder} -type f \\( {extensions_str} \\) ! -path '*/.*' ! -name '_*'"
        
        if args.ignore:
            ignore_files = args.ignore.split(',')
            ignore_str = ' '.join([f"! -name '{file}'" for file in ignore_files])
            command += f" {ignore_str}"
        
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        
        # Split the output into a list of file paths
        file_paths = output.strip().split('\n')
        print()
        print(colored(f"command {command}", 'cyan'))
        print(colored(f"file_paths {file_paths}", 'yellow'))
        print()
        
        # Iterate through each file path
        for file_path in file_paths:
            file_num += 1
            
            all_files_currently.add(file_path)

            content = ""
            with open(file_path, 'r') as file:
                content = file.read()


            # Check if the file content changed
            if file_path in processed_files:
                processed_file_num = processed_files[file_path]
                if content == hashtags_for_all[ processed_file_num ]['content']:
                    print(f"Skipping file: {file_path} | number {processed_file_num} (content unchanged)")
                    continue
            
            # Do something with each file path
            print(f"{file_num} --- Processing file: {file_path}")
            
            amount_of_hashtags = min(85, max(8, int(len(content)/500)))
            short_info = [content]
            if len(content) < 600:
                print("File is small, just list contents.")
            else: # or else get hashtags
                print("     We'll request AI for tags in 3s")
                time.sleep(3)
                print("     Requested..")
                message = client.messages.create(
                    model=model,
                    max_tokens=2000,
                    temperature=0.1,
                    system="Blockchain noderunner/developer making a Python tuple of hashtags",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": """<document_content>""" + content + """</document_content>

People are looking for information and we need to help them find relevant info. Read the document and create decorrelated hashtags based on your understanding of what topics are special in its content and make it unique.
Forbidden words in tags: Namada, Blockchain. Hashtags shouldn't include # sign, only words."""
                                }
                            ]
                        },
                        {"role": "assistant", "content": """Here's a Python tuple of """+ str(amount_of_hashtags) +""" unique-meaning one-word title case (except for acronyms that are uppercase) hashtags. To produce the most useful hashtags possible, we never include more than 3 words in a hashtag and we focus on the core and key concepts that make the provided document unique.
tags=(\""""}
                    ]
                )
                txt = message.content[0].text
                print(txt)
                print("len", len(content), len(txt))
                print("amount_of_hashtags", amount_of_hashtags)
                print(message.usage)
                total_usage += message.usage.input_tokens + message.usage.output_tokens
                print("Total TOKENS used this run", total_usage)
                if len(content) > len(txt)*3:
                    short_info = ast.literal_eval("(\"" + txt)
                

            key_num = file_num
            if file_path in processed_files:
                key_num = processed_files[file_path]
            else:
                while str(key_num) in hashtags_for_all:
                    key_num += 1

            print(file_num,"file_num. In JSON is under entry", key_num)

            hashtags_for_all[str(key_num)] = {
                "file": file_path,
                "tags": short_info,
                "content": content
            }
            processed_files[file_path] = str(key_num)
            print()

            # Write the JSON data to the specified output file
            with open(args.output, 'w') as output_file:
                json.dump(hashtags_for_all, output_file, indent=2)
            
            
    
    # Remove files from the JSON that are not listed in the selected folders
    if args.truncate:
        # Iterate over a copy of the dictionary to avoid modifying the original during iteration
        for key, value in list(hashtags_for_all.items()):
            # Check if the "file" value is not present in the set of files
            if value["file"] not in all_files_currently:
                # If the file is not present, remove the entry from the dictionary
                removed_entry = hashtags_for_all.pop(key)
                print(colored(f"removing the (old) { removed_entry } from the JSON, due to not existing in a new list of files + truncation option being selected", "red"))

        # Write the JSON data to the specified output file after truncating
        with open(args.output, 'w') as output_file:
            json.dump(hashtags_for_all, output_file, indent=2)
else:
    print("No folders provided. Please use the --folders parameter to specify the folders to process.")