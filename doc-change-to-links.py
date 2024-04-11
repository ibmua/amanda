"""
python3 doc-change-to-links.py --input "outputs/asking-ai.prompt" > outputs/asking-ai-http-docs.prompt
"""

import argparse
import re

def parse_file(input_file):
    with open(input_file, 'r') as file:
        content = file.read()

    pattern = re.compile(r'<source>namada-src/namada-docs/packages/docs/pages/(.*?)\.mdx</source>')
    parsed_content = pattern.sub(r'<source>https://docs.namada.net/\1</source>', content)

    content = parsed_content

    pattern = re.compile(r'<source>namada-src/namada-docs/packages/specs/pages/(.*?)\.mdx</source>')
    parsed_content = pattern.sub(r'<source>https://specs.namada.net/\1</source>', content)

    content = parsed_content

    pattern = re.compile(r'<source>namada-src/namada-docs/packages/community/pages/(.*?)\.mdx</source>')
    parsed_content = pattern.sub(r'<source>https://namada.net/community/\1</source>', content)

    return parsed_content

def main():
    parser = argparse.ArgumentParser(description='Parse input file and replace source tags.')
    parser.add_argument('--input', type=str, required=True, help='Input file path')
    args = parser.parse_args()

    parsed_content = parse_file(args.input)
    print(parsed_content)

if __name__ == '__main__':
    main()