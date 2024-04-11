#!/usr/bin/env python3
"""
Usage:
python3 parse-template.py  --template templates/file-filter-request.template  --question outputs/question  --hashtags hashtags/feed-to-ai.json  --output outputs/file-filter.prompt
python3 parse-template.py  --template templates/file-filter-refinement-phase.template  --question outputs/question  --hashtags outputs/response-of-the-file-filter_non-zero.json  --output outputs/files-refined.prompt


Problem Statement:
This script parses a template file containing prompts, document paths within the <documents> section, a <HASHTAGS/> tag,
a <SMALL_FILES/> tag, and a <QUESTION/> tag. It executes the prompts, retrieves the content of the documents, processes
the hashtags file, replaces the <HASHTAGS/> tag with a list of unique hashtags, replaces the <SMALL_FILES/> tag with the
content of small files, replaces the <QUESTION/> tag with the contents of the specified question file, and generates an
output file with the updated documents section, the list of unique hashtags, the content of small files, and the question
content. It displays progress interactively during the execution of prompts and document processing.

Algorithm:
1. Parse command-line arguments to get the template file path, output file path, hashtags file path (optional), and question file path (optional)
2. Read the template file content
3. Process the template content:
   - Extract items (prompts and document paths) from the <documents> section
   - Execute the prompts and capture their output
   - Retrieve the content of the documents
   - Update the documents section in the template with the prompt outputs and document contents
   - If the <HASHTAGS/> tag is present and the hashtags file path is provided:
     - Process the hashtags file and generate a list of unique hashtags
     - Replace the <HASHTAGS/> tag with the list of unique hashtags
   - If the <SMALL_FILES/> tag is present and the hashtags file path is provided:
     - Process the hashtags file and retrieve the content of small files
     - Replace the <SMALL_FILES/> tag with the content of small files in the updated format
   - If the <QUESTION/> tag is present and the question file path is provided:
     - Read the contents of the question file
     - Replace the <QUESTION/> tag with the question content
4. Write the processed output to the output file
5. Display progress interactively during the execution of prompts and document processing

The script uses the following functions:
- update_interactively(): Updates the console output interactively using ANSI escape codes
- create_output_text(): Creates the output text for progress display
- display_progress(): Displays the progress of item processing interactively
- execute_prompt(): Executes a prompt command and captures its output
- process_documents(): Processes the items (prompts and document paths) within the <documents> section
- process_hashtags(): Processes the hashtags file and generates a list of unique hashtags
- process_small_files(): Processes the hashtags file and retrieves the content of small files in the updated format

The main() function:
- Parses command-line arguments using argparse
- Reads the template file content
- Processes the template content line by line:
  - Extracts items (prompts and document paths) from the <documents> section
  - Calls process_documents() to process the extracted items
  - Updates the output content with the processed documents section
  - If the <HASHTAGS/> tag is encountered and the hashtags file path is provided:
    - Calls process_hashtags() to process the hashtags file and generate a list of unique hashtags
    - Replaces the <HASHTAGS/> tag with the list of unique hashtags
  - If the <SMALL_FILES/> tag is encountered and the hashtags file path is provided:
    - Calls process_small_files() to process the hashtags file and retrieve the content of small files in the updated format
    - Replaces the <SMALL_FILES/> tag with the content of small files in the updated format
  - If the <QUESTION/> tag is encountered and the question file path is provided:
    - Reads the contents of the question file
    - Replaces the <QUESTION/> tag with the question content
- Writes the processed output content to the output file

The script displays progress interactively during the execution of prompts and document processing,
showing the status of each item processing step (e.g., "🏇" for in progress, "✅" for success, "❌" for error).
"""
import argparse
import os
import subprocess
import sys
import time
import json


def update_interactively(previous_text, new_text):
    # Calculate the number of lines to move up
    num_lines = previous_text.count("\n")
    
    # Move the cursor up to the start of the previous text
    sys.stdout.write("\033[{}A".format(num_lines))
    
    # Clear the previous text
    sys.stdout.write("\033[J")
    
    # Print the new text
    print(new_text, end="")
    sys.stdout.flush()

def create_output_text(items_with_statuses):
    output = ""
    for item, status in items_with_statuses:
        output += f"{status} {item}\n"
    return output

def display_progress(items, process_item):
    items_with_statuses = [(item, "  ") for item in items]
    output = create_output_text(items_with_statuses)
    print(output, end="")
    sys.stdout.flush()
    
    for i, item in enumerate(items):
        items_with_statuses[i] = (item, "🏇")
        output = create_output_text(items_with_statuses)
        update_interactively(output, output)
        
        status = process_item(item)
        items_with_statuses[i] = (item, status)
        output = create_output_text(items_with_statuses)
        update_interactively(output, output)

def execute_prompt(prompt):
    try:
        output = subprocess.check_output(prompt, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return "✅", output
    except subprocess.CalledProcessError as e:
        return "❌", e.output

def process_documents(items):
    updated_documents_section = ""
    
    def process_item(item):
        prompt_start = item.lower().find("<prompt>")
        if prompt_start != -1:
            prompt_end = item.lower().find("</prompt>", prompt_start + 8)
            if prompt_end != -1:
                prompt = item[prompt_start + 8:prompt_end].strip()
                status, output = execute_prompt(prompt)
                return status
        else:
            document_path = item.replace("<DOCUMENT_PATH>", "").replace("</DOCUMENT_PATH>", "").strip()
            document_path = os.path.expanduser(document_path)
            try:
                with open(document_path, "r") as file:
                    content = file.read()
                return "✅"
            except IOError as e:
                return f"❌ Error: {str(e)}"
    
    display_progress(items, process_item)
    
    for i, item in enumerate(items, start=1):
        prompt_start = item.lower().find("<prompt>")
        if prompt_start != -1:
            prompt_end = item.lower().find("</prompt>", prompt_start + 8)
            if prompt_end != -1:
                prompt = item[prompt_start + 8:prompt_end].strip()
                status, output = execute_prompt(prompt)
                updated_documents_section += f"<document index=\"{i}\">\n<source>CLI:\n{prompt}\n</source>\n<document_content>\n{output}\n</document_content>\n</document>\n"
        else:
            document_path = item.replace("<DOCUMENT_PATH>", "").replace("</DOCUMENT_PATH>", "").strip()
            document_path = os.path.expanduser(document_path)
            try:
                with open(document_path, "r") as file:
                    content = file.read()
                updated_documents_section += f"<document index=\"{i}\">\n<source>{document_path}</source>\n<document_content>\n{content}\n</document_content>\n<source>{document_path}</source>\n</document>\n"
            except IOError as e:
                updated_documents_section += f"<document index=\"{i}\">\n<source>{document_path}</source>\n<document_content>\nError: {str(e)}\n</document_content>\n<source>{document_path}</source>\n</document>\n"
    
    return updated_documents_section

def process_hashtags(hashtags_file):
    try:
        with open(hashtags_file, "r") as file:
            # hashtags_data = json.load(file)
            hashtags_data = file.read()
    except IOError as e:
        return f"Error: {str(e)}"
    
    # unique_hashtags = set()
    # for data in hashtags_data.values():
    #     tags = data.get("tags", [])
    #     if len(tags) >= 3:
    #         unique_hashtags.update(tags)
    
    # hashtags_str = " ".join(f"#{tag}" for tag in unique_hashtags)
    # return hashtags_str
    return hashtags_data
    
def process_small_files(hashtags_file):
    try:
        with open(hashtags_file, "r") as file:
            hashtags_data = json.load(file)
    except IOError as e:
        return f"Error: {str(e)}"
    
    small_files_str = ""
    for num, data in hashtags_data.items():
        tags = data.get("tags", [])
        if len(tags) <= 1:
            content = data["content"]
            file = data["file"]
            small_files_str += f"<document index={num}>\n<source>{file}</source>\n<document_content>\n{content}\n</document_content></document>\n"
    
    return small_files_str

def main():
    parser = argparse.ArgumentParser(description="Process a template file and generate an output file.")
    parser.add_argument("--template", required=True, help="Path to the template file")
    parser.add_argument("--output", required=True, help="Path to the output file")
    parser.add_argument("--hashtags", help="Path to the hashtags JSON file")
    parser.add_argument("--question", help="Path to the question file")
    args = parser.parse_args()
    
    with open(args.template, "r") as file:
        template_content = file.read()
    
    output_content = ""
    items = []
    processing_documents = False
    
    for line in template_content.split("\n"):
        if line.lower().startswith("<documents>"):
            processing_documents = True
            output_content += line + "\n"
        elif line.lower().startswith("</documents>"):
            processing_documents = False
            updated_documents_section = process_documents(items)
            output_content += updated_documents_section
            output_content += line + "\n"
            items = []
        elif line.lower().startswith("<hashtags/>"):
            if args.hashtags:
                hashtags_str = process_hashtags(args.hashtags)
                output_content += hashtags_str + "\n"
            else:
                output_content += line + "\n"
        elif line.lower().startswith("<small_files/>"):
            if args.hashtags:
                small_files_str = process_small_files(args.hashtags)
                output_content += small_files_str + "\n"
            else:
                output_content += line + "\n"
        elif line.lower().startswith("<question/>"):
            if args.question:
                with open(args.question, "r") as file:
                    question_content = file.read()
                output_content += f"<question>{question_content}</question>\n"
            else:
                output_content += line + "\n"
        else:
            if processing_documents:
                prompt_start = line.lower().find("<prompt>")
                if prompt_start != -1:
                    prompt_end = line.lower().find("</prompt>", prompt_start + 8)
                    if prompt_end != -1:
                        items.append(line)
                elif line.lower().startswith("<document_path>"):
                    items.append(line)
            else:
                output_content += line + "\n"
    
    with open(args.output, "w") as file:
        file.write(output_content)

if __name__ == "__main__":
    main()