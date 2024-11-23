#!/usr/bin/env python3

import os
import sys
import subprocess
from anthropic import Anthropic

def run_bash_command(command: str) -> tuple[str, str]:
    """Run a bash command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)

def process_bash_command(command: str) -> int:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=api_key)

    try:
        system_message = """You are a bash command assistant that executes commands through the bash tool.

For SQLite database queries:
1. When asked to show/list/display tables in app.db, you MUST execute: sqlite3 app.db .tables
2. When asked about schema in app.db, you MUST execute: sqlite3 app.db .schema
3. When asked to query data in app.db, you MUST execute: sqlite3 app.db "SELECT * FROM table_name;"

Guidelines:
- ALWAYS use the bash tool to execute commands
- For SQLite queries, use EXACTLY the commands above
- Do not modify or parse database names - use them exactly as given
- Do not try to explain what you will do - just execute the command"""

        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_message,
            tools=[{
                "type": "bash_20241022",
                "name": "bash"
            }],
            messages=[{
                "role": "user", 
                "content": command
            }],
            tool_choice={"type": "tool", "name": "bash"},
            betas=["computer-use-2024-10-22"]
        )

        # Process tool calls
        for content in response.content:
            if content.type == 'text':
                print("\nClaude:", content.text)
            elif content.type == 'tool_use':
                if content.name == 'bash':
                    cmd = content.input.get('command')
                    if cmd:
                        print(f"\nExecuting: {cmd}")
                        stdout, stderr = run_bash_command(cmd)
                        if stdout:
                            print("\nOutput:", stdout)
                        if stderr:
                            print("\nErrors:", stderr, file=sys.stderr)
                        return 0

        print("\nNo bash command was executed. Please try rephrasing your request.")
        return 1

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def interactive_mode():
    print("Interactive Bash Command Mode")
    print("Enter your commands in natural language (type 'exit' to quit)")
    print("----------------------------------------")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not command:
                continue
                
            process_bash_command(command)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) == 2:
        exit_code = process_bash_command(sys.argv[1])
        sys.exit(exit_code)
    else:
        print("Usage: bash_processor.py [\"<command>\"]", file=sys.stderr)
        print("       If no command is provided, enters interactive mode", file=sys.stderr)
        sys.exit(1)
