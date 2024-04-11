"""
python3 display-markdown.py --input outputs/ai-answer.md
"""
import argparse
from rich.console import Console
from rich.markdown import Markdown

def display_markdown(file_path):
    console = Console()
    with open(file_path, 'r') as f:
        md = Markdown(f.read())
        console.print(md)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display markdown file in the terminal.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input markdown file.')
    args = parser.parse_args()

    print()
    print()
    display_markdown(args.input)
    print()
    print()