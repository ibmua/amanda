"""
Logic
    echo "" > outputs/cli-commands
    parallel for i while help/help-descriptions-and-ids.json.$i files are available:
        python3 parse-template.py --template templates/cli.template --question outputs/question --hashtags help/help-descriptions-and-ids.json.$i --output outputs/cli.prompt.$i
        python3 AI-request.py --model haiku --max-tokens 4096 --temperature 0.1 --system system-request-json --message-user outputs/cli.prompt.$i --message-assistant response-start-json --api anthropic > outputs/about-cli.response.$i
        cat response-start-json > outputs/about-cli-response.json.$i
        cat outputs/about-cli.response >> outputs/about-cli-response.json.$i

    sequential for i while help/help-descriptions-and-ids.json.$i files are available:
        python3 cli-picked-useful.py --cli-response-json outputs/about-cli-response.json.$i --cli-desc-and-ids-json help/help-descriptions-and-ids.json --full-cli-json "help/namada-help.json" >> outputs/cli-commands

usage
    python3 cli-gen.py
"""

import os
import subprocess
import json
from multiprocessing import Pool

# Get the directory path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Clear the contents of outputs/cli-commands file
with open(os.path.join(script_dir, 'outputs/cli-commands'), 'w') as f:
    f.write('')

def process_file(i):
    help_file = os.path.join(script_dir, f'help/help-descriptions-and-ids.json.{i}')
    if not os.path.isfile(help_file):
        return

    # Run parse-template.py
    subprocess.run([
        'python3', os.path.join(script_dir, 'parse-template.py'),
        '--template', os.path.join(script_dir, 'templates/cli.template'),
        '--question', os.path.join(script_dir, 'outputs/question'),
        '--hashtags', help_file,
        '--output', os.path.join(script_dir, f'outputs/cli.prompt.{i}')
    ])

    # Run AI-request.py
    with open(os.path.join(script_dir, f'outputs/about-cli.response.{i}'), 'w') as f:
        subprocess.run([
            'python3', os.path.join(script_dir, 'AI-request.py'),
            '--model', 'haiku',
            '--max-tokens', '4096',
            '--temperature', '0.1',
            '--system', 'system-request-json',
            '--message-user', os.path.join(script_dir, f'outputs/cli.prompt.{i}'),
            '--message-assistant', 'response-start-json',
            # '--api', 'anthropic'
        ], stdout=f)

    # Write response-start-json and the contents of about-cli.response to about-cli-response.json
    with open(os.path.join(script_dir, 'response-start-json')) as f:
        response_start_json = f.read()
    with open(os.path.join(script_dir, f'outputs/about-cli.response.{i}')) as f:
        about_cli_response = f.read()
    with open(os.path.join(script_dir, f'outputs/about-cli-response.json.{i}'), 'w') as f:
        f.write(response_start_json + about_cli_response)

if __name__ == '__main__':
    # Get the number of available help/help-descriptions-and-ids.json.$i files
    num_files = len([f for f in os.listdir(os.path.join(script_dir, 'help')) if f.startswith('help-descriptions-and-ids.json.')])

    # Process files in parallel
    with Pool() as pool:
        pool.map(process_file, range(num_files))

    # Process files sequentially
    for i in range(num_files):
        with open(os.path.join(script_dir, 'outputs/cli-commands'), 'a') as f:
            subprocess.run([
                'python3', os.path.join(script_dir, 'cli-picked-useful.py'),
                '--cli-response-json', os.path.join(script_dir, f'outputs/about-cli-response.json.{i}'),
                '--cli-desc-and-ids-json', os.path.join(script_dir, 'help/help-descriptions-and-ids.json'),
                '--full-cli-json', os.path.join(script_dir, 'help/namada-help.json')
            ], stdout=f)