#!/usr/bin/env python3

import os
import sys
import asyncio
import pyautogui
import webbrowser
import urllib.parse
from uuid import uuid4

# Initialize pyautogui safely
pyautogui.FAILSAFE = True  # Move mouse to upper-left to abort
pyautogui.PAUSE = 0.1  # Add small delay between actions

# Constants
TYPING_DELAY_MS = 12

async def execute_computer_action(command: str) -> str:
    """Execute a computer action based on the command."""
    try:
        # Parse the command
        parts = command.lower().split()
        
        if 'type' in parts:
            # Get the text after "type"
            text = command[command.lower().index('type') + 5:].strip()
            if not text:
                return "No text provided for typing"
            
            print(f"\nWARNING: About to type '{text}' in 3 seconds...")
            print("Move mouse to upper-left corner to cancel")
            await asyncio.sleep(3)  # Give user time to cancel
            
            try:
                # Type the text with natural delays
                pyautogui.write(text, interval=TYPING_DELAY_MS/1000)
                return f"Successfully typed: {text}"
            except Exception as e:
                return f"Failed to type text: {str(e)}"

        elif 'search' in parts:
            # Get the search query after "search"
            query = command[command.lower().index('search') + 7:].strip()
            if not query:
                return "No search query provided"
            
            # Encode the query for URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            print(f"\nWARNING: About to open browser search for '{query}' in 3 seconds...")
            await asyncio.sleep(3)  # Give user time to cancel
            
            try:
                webbrowser.open(search_url)
                return f"Successfully opened search for: {query}"
            except Exception as e:
                return f"Failed to open browser: {str(e)}"

        elif 'screenshot' in parts:
            # Create screenshots directory if it doesn't exist
            screenshot_dir = os.path.join(os.getcwd(), "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Take screenshot
            timestamp = uuid4().hex
            filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            
            try:
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)
                return f"Screenshot saved to {filename}"
            except Exception as e:
                return f"Failed to take screenshot: {str(e)}"

        elif 'click' in parts:
            print("\nWARNING: About to click in 3 seconds...")
            print("Move mouse to upper-left corner to cancel")
            await asyncio.sleep(3)
            
            try:
                if 'right' in parts:
                    pyautogui.rightClick()
                    return "Successfully right clicked"
                elif 'double' in parts:
                    pyautogui.doubleClick()
                    return "Successfully double clicked"
                else:
                    pyautogui.click()
                    return "Successfully left clicked"
            except Exception as e:
                return f"Failed to click: {str(e)}"

        elif 'move' in parts and 'mouse' in parts:
            # Look for numbers in the command
            numbers = [int(s) for s in parts if s.isdigit()]
            if len(numbers) >= 2:
                x, y = numbers[0], numbers[1]
                
                print(f"\nWARNING: About to move mouse to ({x}, {y}) in 3 seconds...")
                print("Move mouse to upper-left corner to cancel")
                await asyncio.sleep(3)
                
                try:
                    pyautogui.moveTo(x, y, duration=0.25)
                    return f"Successfully moved mouse to ({x}, {y})"
                except Exception as e:
                    return f"Failed to move mouse: {str(e)}"
            else:
                return "Please provide x and y coordinates for mouse movement"

        else:
            return f"Unknown command. Available commands: type <text>, search <query>, screenshot, click, right click, double click, move mouse <x> <y>"

    except Exception as e:
        print(f"Error executing command: {str(e)}", file=sys.stderr)
        return f"Error executing command: {str(e)}"

async def main(command: str) -> int:
    try:
        result = await execute_computer_action(command)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

def interactive_mode():
    print("Interactive Computer Control Mode")
    print("Available commands:")
    print("  type <text>           - Type the specified text")
    print("  search <query>       - Open browser search for the query")
    print("  screenshot            - Take a screenshot")
    print("  click                 - Perform a left click")
    print("  right click          - Perform a right click")
    print("  double click         - Perform a double click")
    print("  move mouse <x> <y>   - Move mouse to coordinates")
    print("  exit                 - Exit the program")
    print("----------------------------------------")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not command:
                continue
                
            asyncio.run(main(command))
            
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
        exit_code = asyncio.run(main(command))
        sys.exit(exit_code)
    else:
        print("Usage: computer_processor.py [command]", file=sys.stderr)
        print("       If no command is provided, enters interactive mode", file=sys.stderr)
        sys.exit(1)
