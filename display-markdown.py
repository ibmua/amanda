import argparse
import re
from rich.console import Console
from rich.markdown import Markdown

try:
    import IPython
    if 'google.colab' in str(IPython.get_ipython()):
        is_colab = True
        is_jupyter = False
    else:
        is_colab = False
        is_jupyter = IPython.get_ipython() is not None
except (ImportError, NameError):
    is_colab = False
    is_jupyter = False

def display_markdown(file_path):
    console = Console()
    with open(file_path, 'r') as f:
        content = f.read()
    if is_colab or is_jupyter:
        # Replace links with plain text URLs in Colab or Jupyter
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', content)
    md = Markdown(content)
    if is_colab or is_jupyter:
        # Print the Markdown content as plain text in Colab or Jupyter
        print(md.plain)
    else:
        # Print the formatted Markdown in the terminal
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