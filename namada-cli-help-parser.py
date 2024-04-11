#!/usr/bin/env python3

# REQUIRED: 
# pip3 install termcolor

# Usage:
# python3 namada-cli-help-parser.py --output-full help/namada-help.json --output-description help/help-descriptions-only.json --commands namada osmosisd
# python3 namada-cli-help-parser.py [--output-full OUTPUT_FULL] [--output-description OUTPUT_DESCRIPTION] [--commands COMMAND1 COMMAND2 ...]

#
# Problem Statement:
# This script generates JSON files containing the help output for all valid commands in the `namada` program.
# It performs a depth-first search on the available commands and subcommands, retrieving the help output for each command.
# The resulting JSON files will have a structure where the keys are the command names and the values are the corresponding help outputs.
#
# Algorithm:
# 1. Define a `get_help_output` function that takes a command as input, runs it with the `--help` flag, and returns the help output.
#    If the command is invalid, it returns `None`.
# 2. Define a `traverse_commands` function that performs a depth-first search on the available commands.
#    - For each command, it constructs the full command by appending it to the `base_command`, retrieves the help output, and adds it to the `result_full` and `result_description` dictionaries.
#    - If the help output contains a "Commands:" section, it extracts the sub-commands and recursively calls `traverse_commands` with the updated `base_command` and sub-commands.
# 3. Define a `minimize_json_data` function that takes a JSON object as input and minimizes the help output by removing unnecessary whitespace, usage, and options sections.
# 4. In the `main` function:
#    - Parse the command-line arguments `--output-full` and `--output-description` using `argparse` to get the output file paths.
#    - Start with the base command `["namada"]` and empty `result_full` and `result_description` dictionaries.
#    - Retrieve the help output for the base command, add it to `result_full`, and add the minimized version to `result_description`.
#    - Extract the top-level commands from the help output and call `traverse_commands` with the base command, top-level commands, and the `result_full` and `result_description` dictionaries.
#    - If `--output-full` is provided, write the `result_full` dictionary to the specified JSON file.
#    - If `--output-description` is provided, write the `result_description` dictionary to the specified JSON file.
#
# The script uses the following functions:
# - `get_help_output()`: Runs a command with the `--help` flag and returns the help output or `None` if the command is invalid.
# - `traverse_commands()`: Performs a depth-first search on the available commands and subcommands, retrieving the help output for each command and populating the `result_full` and `result_description` dictionaries.
# - `minimize_json_data()`: Minimizes the help output by removing unnecessary whitespace, usage, and options sections.
#
# The `main()` function:
# - Parses the command-line arguments `--output-full` and `--output-description` using `argparse` to get the output file paths.
# - Starts with the base command `["namada"]` and empty `result_full` and `result_description` dictionaries.
# - Retrieves the help output for the base command, adds it to `result_full`, and adds the minimized version to `result_description`.
# - Extracts the top-level commands from the help output and calls `traverse_commands` with the base command, top-level commands, and the `result_full` and `result_description` dictionaries.
# - If `--output-full` is provided, writes the `result_full` dictionary to the specified JSON file.
# - If `--output-description` is provided, writes the `result_description` dictionary to the specified JSON file.
#

import json
import subprocess
import argparse
from collections import deque
from termcolor import colored
import re

MAX_DEPTH = 3
MAX_COMMANDS = 1500

def get_help_output(command):
    print(colored(f"Running command: {' '.join(command)}", "cyan"))
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        print(colored(f"Command output:\n{output}\n", "green"))
        return output.strip()
    except subprocess.CalledProcessError as e:
        print(colored(f"Command failed with error:\n{e}\n", "red"))
        return None

def is_valid_command(command):
    return not command.startswith("-") and command.lower() != "help" and command.lower() != "options:"

def extract_commands(output):
    commands = []
    if "Available Commands:" in output:
        # Extract commands for the first input format
        commands_section = output.split("Available Commands:")[1].strip()
        for line in commands_section.split("\n"):
            if not line.startswith("Flags:") and not line.startswith("Global Flags:") and not line.startswith("Use"):
                command = line.strip().split(" ")[0]
                if is_valid_command(command):
                    commands.append(command)
    else:
        # Extract commands for the second input format
        for line in output.split("\n"):
            if line.startswith("  "):
                command = line.strip().split(" ")[0]
                if is_valid_command(command):
                    commands.append(command)
    return commands

def normalize_command(command):
    return ' '.join(command.split())

def traverse_commands(base_command, commands, result_full, result_description, processed_commands, parent_output, depth=0, command_count=0):
    if depth > MAX_DEPTH:
        print(colored(f"Maximum depth of {MAX_DEPTH} reached. Stopping traversal.", "red"))
        return command_count

    if command_count > MAX_COMMANDS:
        print(colored(f"Maximum command count of {MAX_COMMANDS} reached. Stopping traversal.", "red"))
        return command_count

    for command in commands:
        if not is_valid_command(command):
            print(colored(f"Skipping invalid command: {command}", "magenta"))
            continue

        full_command = normalize_command(" ".join(base_command + [command]))
        if full_command in processed_commands:
            print(colored(f"Command already processed: {full_command}", "magenta"))
            continue

        print(colored(f"Processing command: {full_command}", "yellow"))
        print(colored(f"Retrieving help for command: {full_command}", "magenta"))
        output = get_help_output(base_command + [command] + ["--help"])
        if output:
            if output == parent_output:
                print(colored(f"Skipping invalid command (same output as parent): {full_command}", "magenta"))
                continue

            result_full[full_command] = output
            result_description[full_command] = minimize_json_data({full_command: output})[full_command]
            command_count += 1
            processed_commands.add(full_command)

            sub_commands = extract_commands(output)
            if sub_commands:
                print(colored(f"Found sub-commands: {', '.join(sub_commands)}", "blue"))
                command_count = traverse_commands(base_command + [command], sub_commands, result_full, result_description, processed_commands, output, depth + 1, command_count)
            else:
                print(colored("No sub-commands found.", "blue"))
        else:
            print(colored("Failed to retrieve help output.", "red"))

    return command_count
    
def minimize_json_data(json_data):
    minimized_data = {}

    for key, value in json_data.items():
        # Remove leading/trailing whitespace
        minimized_value = value.strip()

        # Remove multiple consecutive whitespace
        minimized_value = re.sub(r'\s+', ' ', minimized_value)

        # Remove usage and options sections
        minimized_value = re.sub(r'Usage: .*', '', minimized_value, flags=re.DOTALL)
        minimized_value = re.sub(r'Options:.*', '', minimized_value, flags=re.DOTALL)

        # Remove empty lines
        minimized_value = re.sub(r'\n\s*\n', '\n', minimized_value)

        minimized_data[key] = minimized_value.strip()

    return minimized_data

def main():
    parser = argparse.ArgumentParser(description="Generate JSON files containing help output for specified commands")
    parser.add_argument("--output-full", help="Output JSON file path for the full help output")
    parser.add_argument("--output-description", help="Output JSON file path for the minimized help output")
    parser.add_argument("--commands", nargs="+", help="List of commands to scan help for", default=["namada"])
    args = parser.parse_args()

    result_full = {}
    result_description = {}
    processed_commands = set()

    for base_command in args.commands:
        print(colored(f"Retrieving help for base command: {base_command}", "cyan"))
        output = get_help_output([base_command, "--help"])
        if output:
            normalized_base_command = normalize_command(base_command)
            result_full[normalized_base_command] = output
            result_description[normalized_base_command] = minimize_json_data({normalized_base_command: output})[normalized_base_command]
            commands = extract_commands(output)
            print(colored(f"Found top-level commands for {base_command}: {', '.join(commands)}", "blue"))
            command_count = traverse_commands([base_command], commands, result_full, result_description, processed_commands, output)
            print(colored(f"Total commands parsed for {base_command}: {command_count}", "green"))
        else:
            print(colored(f"Failed to retrieve help output for base command: {base_command}", "red"))

    if args.output_full:
        print(colored(f"Writing full output to file: {args.output_full}", "green"))
        with open(args.output_full, "w") as outfile:
            json.dump(result_full, outfile, indent=2)

    if args.output_description:
        print(colored(f"Writing minimized output to file: {args.output_description}", "green"))
        with open(args.output_description, "w") as outfile:
            json.dump(result_description, outfile, indent=2)

    print(colored("Script execution completed.", "green"))

if __name__ == "__main__":
    main()
