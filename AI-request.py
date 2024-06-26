#!/usr/bin/env python3
"""
AI-request.py

This script sends a message to Claude using the Anthropic API, taking the API parameters, system message, user message, and assistant message as command-line arguments.

Usage:
    python3 AI-request.py --model MODEL --max-tokens MAX_TOKENS --temperature TEMPERATURE --system SYSTEM_FILE --message-user USER_FILE --message-assistant ASSISTANT_FILE
    python3 AI-request.py --model haiku --max-tokens 4096 --temperature 0.1 --system system-request-json --message-user outputs/file-filter.prompt --message-assistant response-start-json > outputs/response-of-the-file-filter
    python3 AI-request.py --model haiku --max-tokens 4096 --temperature 0.1 --system system-request-json --message-user "outputs/file-filter.prompt.${i}" --message-assistant response-start-json >> "outputs/response-of-the-file-filter.${i}"

Arguments:
    --model             Anthropic model to use: "sonnet", "opus", or "haiku" (default: "sonnet")
    --max-tokens        Maximum number of tokens in the API response
    --temperature       Temperature value for the API request
    --system            File containing the system message
    --message-user      File containing the user message
    --message-assistant File containing the assistant message

Environment Variables:
    CLAUDE_API_KEY      Anthropic API key
    GOOGLE_PROJECT_ID   Google Cloud project ID (required when using the Google API)
    AMANDA_API          API to use: "anthropic" or "google" (default: "anthropic")
"""

import os
import anthropic
import argparse
import random

# regions = ["us-central1", "asia-southeast1", "europe-west4"]
regions = ["us-central1"]
selected_region = random.choice(regions)

# Create an argument parser
parser = argparse.ArgumentParser(description='Send a message to Claude using the Anthropic API.')
parser.add_argument('--model', type=str, help='Anthropic model to use: "sonnet", "opus", or "haiku" (default: "sonnet")', default='sonnet')
parser.add_argument('--max-tokens', type=int, help='Maximum number of tokens in the API response', required=True)
parser.add_argument('--temperature', type=float, help='Temperature value for the API request', required=True)
parser.add_argument('--system', type=str, help='File containing the system message', required=True)
parser.add_argument('--message-user', type=str, help='File containing the user message', required=True)
parser.add_argument('--message-assistant', type=str, help='File containing the assistant message', default='')
args = parser.parse_args()

# Get the Anthropic API key from the environment variable
api_key = os.environ.get('CLAUDE_API_KEY')
if not api_key:
    raise ValueError('CLAUDE_API_KEY environment variable is not set.')

# Get the API to use from the environment variable
api = os.environ.get('AMANDA_API', 'anthropic')

# Set up the Anthropic or Google Vertex client based on the AMANDA_API environment variable
if api == 'anthropic':
    client = anthropic.Anthropic(api_key=api_key)
elif api == 'google':
    from anthropic import AnthropicVertex
    project_id = os.environ.get('GOOGLE_PROJECT_ID')
    if not project_id:
        raise ValueError('GOOGLE_PROJECT_ID environment variable is not set.')
    client = AnthropicVertex(region=selected_region, project_id=project_id)
else:
    raise ValueError(f"Invalid API: {api}. Choose 'anthropic' or 'google'.")

# Set the Anthropic model based on the --model argument
if api == 'anthropic':
    if args.model == 'sonnet':
        model = "claude-3-5-sonnet-20240620"
    elif args.model == 'opus':
        model = "claude-3-opus-20240229"
    elif args.model == 'haiku':
        model = "claude-3-haiku-20240307"
    else:
        raise ValueError(f"Invalid model: {args.model}. Choose 'sonnet', 'opus', or 'haiku'.")
else:  # Google API
    if args.model == 'sonnet':
        model = "claude-3-5-sonnet-20240620"
    elif args.model == 'opus':
        model = "claude-3-opus@20240229"
    elif args.model == 'haiku':
        model = "claude-3-haiku@20240307"
    else:
        raise ValueError(f"Invalid model: {args.model}. Choose 'sonnet', 'opus', or 'haiku'.")

# Read the contents of the system, user, and assistant message files
with open(args.system, 'r') as file:
    system_message = file.read().strip()

with open(args.message_user, 'r') as file:
    user_message = file.read().strip()

if args.message_assistant != "":
    with open(args.message_assistant, 'r') as file:
        assistant_message = file.read().strip()
else:
    assistant_message = ""


# Send the message to Claude
response = client.messages.create(
    model=model,
    max_tokens=args.max_tokens,
    temperature=args.temperature,
    system=system_message,
    messages=[
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message}
    ]
)

# Print the response from Claude
print(response.content[0].text)