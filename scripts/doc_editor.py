#!/usr/bin/env python3

import os
import sys
import anthropic
from pathlib import Path
import re

def load_env():
    """Load environment variables from .env file."""
    script_dir = Path(__file__).resolve().parent
    env_path = script_dir.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def read_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path, content):
    """Write content to a file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_editor_command(instruction):
    """Process an editor command and extract input/output files."""
    # Use regex to find files after "read" and "Create"
    input_match = re.search(r'read\s+([^\s.]+(?:\.[^\s.]+)*)', instruction)
    output_matches = re.finditer(r'Create\s+([^\s.]+(?:\.[^\s.]+)*)', instruction)
    
    input_file = input_match.group(1) if input_match else None
    output_files = [m.group(1) for m in output_matches]
    
    return input_file, output_files, instruction

def edit_document(client, input_file, output_files, instruction):
    """Use Claude to edit/create a document based on instructions."""
    
    # Read input file if it exists
    input_content = ""
    if input_file and os.path.exists(input_file):
        input_content = read_file(input_file)
        
    # Construct the prompt
    prompt = f"""You are a technical documentation editor specializing in creating clear, well-structured documentation. Your task is to:

1. Read and understand the input content below
2. Create new documents that focus specifically on the aspects mentioned in the instruction
3. Format the output in clean markdown with proper headings, code blocks, and sections
4. Remove any irrelevant content or metadata
5. Ensure all code examples are properly formatted with language tags
6. Include only the actual documentation content - no headers about what you're doing
7. Return each document separated by a special marker: ---NEXT_DOC---

Here is the instruction:
{instruction}

Here is the input content to process:

{input_content}

Remember: Provide ONLY the final documentation content for each requested document, properly formatted in markdown, separated by ---NEXT_DOC---. Do not include any meta-text about what you're doing."""

    print("Processing documentation...", file=sys.stderr)
    
    # Get Claude's response
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Extract and clean up the response
    response = message.content[0].text
    
    # Split response into multiple documents if needed
    docs = [doc.strip() for doc in response.split('---NEXT_DOC---')]
    
    # Write each document to its corresponding output file
    for i, output_file in enumerate(output_files):
        if i < len(docs):
            content = docs[i].strip()
            # Remove any meta-text that might appear at the start
            content = re.sub(r'^Here is .*?:\n+', '', content, flags=re.MULTILINE)
            write_file(output_file, content)
            print(f"Created/Updated {output_file}", file=sys.stderr)

def main():
    if len(sys.argv) != 2:
        print("Usage: doc_editor.py \"<instruction>\"", file=sys.stderr)
        sys.exit(1)

    # Load environment variables
    load_env()
    
    # Get ANTHROPIC_API_KEY from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Create Anthropic client
    client = anthropic.Client(api_key=api_key)
    
    # Process the instruction
    instruction = sys.argv[1]
    input_file, output_files, instruction = process_editor_command(instruction)
    
    # Edit/create the document(s)
    edit_document(client, input_file, output_files, instruction)

if __name__ == '__main__':
    main()
