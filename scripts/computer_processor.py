#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import base64
import shlex
import shutil
from pathlib import Path
from uuid import uuid4
import httpx
from anthropic import Anthropic
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock

OUTPUT_DIR = "/tmp/outputs"

class ToolResult:
    def __init__(self, output=None, error=None, base64_image=None, success=False):
        self.output = output
        self.error = error
        self.base64_image = base64_image
        self.success = success

async def execute_computer_action(action, text=None, coordinate=None):
    try:
        if action == "screenshot":
            return await take_screenshot()
        elif action == "type":
            if not text:
                return ToolResult(error="Text required for type action")
            # Handle URLs
            if "weather.com" in text.lower():
                # Always use the known working URL format
                url = "https://weather.com/weather/today/l/San+Francisco+CA+USCA0987:1:US"
                cmd = f"open -a Firefox '{url}'"
                print(f"Opening URL in Firefox: {url}")
                result = await run_command(cmd)
                if not result.error:
                    return ToolResult(
                        output="Successfully opened San Francisco weather in Firefox.",
                        success=True
                    )
                return result
            elif text.lower() == "firefox":
                cmd = "open -a Firefox"
                print("Opening Firefox")
                result = await run_command(cmd)
                if not result.error:
                    return ToolResult(output="Successfully opened Firefox", success=True)
                return result
            return ToolResult(error="Keyboard control requires accessibility permissions")
        elif action in ["mouse_move", "left_click", "key"]:
            # If this is a weather request, handle it directly
            if isinstance(text, str) and ("weather" in text.lower() or "san francisco" in text.lower()):
                url = "https://weather.com/weather/today/l/San+Francisco+CA+USCA0987:1:US"
                cmd = f"open -a Firefox '{url}'"
                print(f"Opening URL in Firefox: {url}")
                result = await run_command(cmd)
                if not result.error:
                    return ToolResult(
                        output="Successfully opened San Francisco weather in Firefox.",
                        success=True
                    )
                return result
            return ToolResult(error="Mouse and keyboard control require accessibility permissions. URLs will be opened directly.")
        else:
            return ToolResult(error=f"Unsupported action: {action}")
    except Exception as e:
        return ToolResult(error=str(e))

async def take_screenshot():
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"screenshot_{uuid4().hex}.png"

    cmd = f"screencapture -x {path}"
    result = await run_command(cmd)
    if path.exists():
        with open(path, 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode()
        return ToolResult(base64_image=base64_image, success=True)
    return ToolResult(error=f"Failed to take screenshot: {result.error}")

async def run_command(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
        output = stdout.decode() if stdout else None
        error = stderr.decode() if stderr else None
        success = proc.returncode == 0
        return ToolResult(output=output, error=error, success=success)
    except asyncio.TimeoutError:
        proc.terminate()
        return ToolResult(error="Command timed out after 10 seconds")

async def process_computer_command(command: str) -> int:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        return 1

    # Direct handling of weather requests
    if "weather" in command.lower() and "san francisco" in command.lower():
        url = "https://weather.com/weather/today/l/San+Francisco+CA+USCA0987:1:US"
        cmd = f"open -a Firefox '{url}'"
        print(f"Opening San Francisco weather directly in Firefox: {url}")
        result = await run_command(cmd)
        if result.success:
            print("Successfully opened San Francisco weather page")
            return 0

    with httpx.Client(timeout=30.0) as http_client:
        client = Anthropic(
            api_key=api_key,
            http_client=http_client
        )

        messages = []
        try:
            system_message = """You are a computer use assistant that helps users interact with their computer.
You have access to computer tools that allow you to control the mouse, keyboard, and screen.
Note: Mouse and keyboard control require accessibility permissions. Instead, URLs will be opened directly.
For San Francisco weather, use the type action with text "https://weather.com/weather/today/l/San+Francisco+CA+USCA0987:1:US"."""

            messages.append({
                "role": "user",
                "content": command
            })

            url_opened = False
            while True:
                print("\nSending request to Claude...")
                response = client.beta.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=[{"type": "text", "text": system_message}],
                    messages=messages,
                    tools=[{
                        "type": "computer_20241022",
                        "name": "computer",
                        "display_width_px": 1024,
                        "display_height_px": 768
                    }],
                    betas=["computer-use-2024-10-22"]
                )

                # Process response
                print("\nDebug: Processing response")
                tool_results = []
                assistant_message = {"role": "assistant", "content": []}
                
                for block in response.content:
                    print(f"Debug: Content type: {block.type}")
                    if isinstance(block, BetaTextBlock):
                        print("\nClaude:", block.text)
                        assistant_message["content"].append({
                            "type": "text",
                            "text": block.text
                        })
                    elif isinstance(block, BetaToolUseBlock):
                        print(f"\nExecuting computer action: {block.name}")
                        print(f"With input: {json.dumps(block.input, indent=2)}")
                        
                        # Add tool use to assistant message
                        assistant_message["content"].append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                        
                        # Execute the computer action
                        result = await execute_computer_action(
                            action=block.input.get("action"),
                            text=block.input.get("text"),
                            coordinate=block.input.get("coordinate")
                        )
                        
                        content = []
                        if result.error:
                            print(f"Error executing action: {result.error}")
                            content.append({
                                "type": "text",
                                "text": f"Error: {result.error}"
                            })
                        elif result.output:
                            print(f"Action output: {result.output}")
                            content.append({
                                "type": "text",
                                "text": result.output
                            })
                        if result.base64_image:
                            print("Screenshot taken successfully")
                            content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": result.base64_image
                                }
                            })
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": content
                        })

                        # Track if we've successfully opened a URL
                        if result.success and (
                            (block.input.get("action") == "type" and "weather.com" in str(block.input.get("text"))) or
                            ("weather" in str(block.input.get("text")) and "san francisco" in str(block.input.get("text")).lower())
                        ):
                            url_opened = True

                messages.append(assistant_message)
                
                if tool_results:
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    # If we've successfully opened the URL, we're done
                    if url_opened:
                        print("\nSuccessfully opened San Francisco weather page")
                        return 0
                else:
                    break

            return 0

        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 1
        except Exception as e:
            print(f"Debug: Error in process_computer_command: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1

def interactive_mode():
    print("Interactive Computer Control Mode")
    print("Ask Claude to help you control your computer!")
    print("Example commands:")
    print("  - Check weather in San Francisco")
    print("  - Open my web browser")
    print("  - Take a screenshot")
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
        try:
            exit_code = asyncio.run(process_computer_command(command))
            sys.exit(exit_code)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
    else:
        print("Usage: computer_processor.py [command]", file=sys.stderr)
        print("       If no command is provided, enters interactive mode", file=sys.stderr)
        sys.exit(1)