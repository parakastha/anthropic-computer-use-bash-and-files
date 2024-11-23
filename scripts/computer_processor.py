#!/usr/bin/env python3

import os
import sys
import json
import asyncio
from anthropic import Anthropic

async def process_computer_command(command: str) -> int:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        return 1

    client = Anthropic(api_key=api_key)

    try:
        system_message = """You are a computer use assistant that helps users interact with their computer.
You have access to computer tools that allow you to control the mouse, keyboard, and screen.
Please help the user by using the computer tools to accomplish their tasks."""

        print("\nSending request to Claude...")
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            system=system_message,
            messages=[{
                "role": "user",
                "content": command
            }],
            tools=[{
                "type": "computer_use",
                "name": "computer"
            }],
            betas=["computer-use"]
        )

        # Process response
        print("\nDebug: Processing response")
        for content in response.content:
            print(f"Debug: Content type: {content.type}")
            if content.type == 'text':
                print("\nClaude:", content.text)
            elif content.type == 'tool_use':
                print(f"\nExecuting computer action: {content.tool_calls[0].name}")
                print(f"With input: {json.dumps(content.tool_calls[0].parameters, indent=2)}")

        return 0

    except Exception as e:
        print(f"Debug: Error in process_computer_command: {str(e)}")
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def interactive_mode():
    print("Interactive Computer Control Mode")
    print("Ask Claude to help you control your computer!")
    print("Example commands:")
    print("  - Search for the weather in San Francisco")
    print("  - Open my web browser")
    print("  - Take a screenshot")
    print("  - Click the button at coordinates 100, 200")
    print("  - Type 'Hello, World!'")
    print("(type 'exit' to quit)")
    print("----------------------------------------")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not command:
                continue
                
            asyncio.run(process_computer_command(command))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            print("\nExiting...")
            break

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) > 1:
        # Join all arguments after the script name as the command
        command = ' '.join(sys.argv[1:])
        exit_code = asyncio.run(process_computer_command(command))
        sys.exit(exit_code)
    else:
        print("Usage: computer_processor.py [command]", file=sys.stderr)
        print("       If no command is provided, enters interactive mode", file=sys.stderr)
        sys.exit(1)
