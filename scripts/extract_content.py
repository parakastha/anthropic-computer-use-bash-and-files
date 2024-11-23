#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import re

def process_code_block(element):
    # Try to find the language from pre or code class
    classes = []
    if element.name == 'pre':
        code_elem = element.find('code')
        if code_elem:
            classes.extend(code_elem.get('class', []))
        classes.extend(element.get('class', []))
    else:
        classes.extend(element.get('class', []))
    
    # Extract language from class names
    language = ''
    for cls in classes:
        if isinstance(cls, str):  # Ensure cls is a string
            if 'language-' in cls:
                language = cls.replace('language-', '')
            elif 'lang-' in cls:
                language = cls.replace('lang-', '')
    
    # Get the code content
    code = element.get_text().strip()
    if code:
        if language:
            return f'```{language}\n{code}\n```'
        else:
            return f'```\n{code}\n```'
    return None

def process_link(element):
    href = element.get('href', '')
    text = element.get_text().strip()
    if href and text:
        return f'[{text}]({href})'
    return text if text else None

def is_heading(tag):
    return tag.name and tag.name.startswith('h') and len(tag.name) == 2 and tag.name[1].isdigit()

def get_heading_level(tag):
    return int(tag.name[1])

def should_skip_element(element):
    if not element:
        return True
    
    # Skip empty elements
    if isinstance(element, NavigableString) and not str(element).strip():
        return True
    
    # Skip hidden elements
    if isinstance(element, Tag):
        style = element.get('style', '')
        if 'display: none' in style or 'visibility: hidden' in style:
            return True
        
        # Skip elements with certain classes or IDs
        classes = element.get('class', [])
        if any(c in classes for c in ['hidden', 'nav', 'menu', 'sidebar', 'footer']):
            return True
    
    return False

def extract_content(url):
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug print
        print(f"Page title: {soup.title.string if soup.title else 'No title'}", file=sys.stderr)
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'button']):
            element.decompose()
        
        # Find the main content area - try multiple selectors
        main = None
        selectors = [
            'main',
            'article',
            '.content',
            '.article',
            '.post',
            '.main',
            '#content',
            '#main',
            '.container',
            '.doc-content',
            '.documentation',
            '[role="main"]'
        ]
        
        for selector in selectors:
            try:
                main = soup.select_one(selector)
                if main:
                    print(f"Found content using selector: {selector}", file=sys.stderr)
                    break
            except Exception as e:
                continue
        
        if not main:
            print("Could not find main content area", file=sys.stderr)
            return None
        
        # Process content recursively
        output = []
        current_heading_level = 0
        in_list = False
        
        def process_element(element, depth=0):
            nonlocal current_heading_level, in_list
            
            # Skip unwanted elements
            if should_skip_element(element):
                return
            
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    output.append(text)
                return
            
            # Handle headings
            if is_heading(element):
                level = get_heading_level(element)
                if level > current_heading_level:
                    current_heading_level = level
                text = element.get_text().strip()
                if text:
                    output.append('\n' + '#' * level + ' ' + text + '\n')
                return
            
            # Handle code blocks
            if element.name in ('pre', 'code'):
                code = process_code_block(element)
                if code:
                    if output and output[-1]:
                        output.append('')
                    output.append(code)
                    if output and output[-1]:
                        output.append('')
                return
            
            # Handle links
            if element.name == 'a':
                link = process_link(element)
                if link:
                    output.append(link)
                return
            
            # Handle lists
            if element.name in ('ul', 'ol'):
                if not in_list:
                    in_list = True
                    if output and output[-1]:
                        output.append('')
                for i, li in enumerate(element.find_all('li', recursive=False)):
                    prefix = '- ' if element.name == 'ul' else f"{i+1}. "
                    text = li.get_text().strip()
                    if text:
                        output.append(prefix + text)
                if not in_list:
                    if output and output[-1]:
                        output.append('')
                in_list = False
                return
            
            # Handle paragraphs and other block elements
            if element.name in ('p', 'div', 'section'):
                if output and output[-1]:  # Add newline between blocks
                    output.append('')
            
            # Recursively process child elements
            for child in element.children:
                process_element(child, depth + 1)
            
            # Add newline after block elements
            if element.name in ('p', 'div', 'section'):
                if output and output[-1]:
                    output.append('')
        
        process_element(main)
        
        # Clean up the output
        text = '\n'.join(output)
        
        # Debug print
        print(f"Raw content length: {len(text)} characters", file=sys.stderr)
        
        lines = []
        current_blank_lines = 0
        for line in text.split('\n'):
            line = line.strip()
            if line:
                if current_blank_lines > 2:
                    current_blank_lines = 1
                for _ in range(current_blank_lines):
                    lines.append('')
                lines.append(line)
                current_blank_lines = 0
            else:
                current_blank_lines += 1
        
        # Remove any remaining navigation text
        filtered_lines = []
        for line in lines:
            # Skip lines that look like navigation
            if re.match(r'^(home|menu|navigation|previous|next|back|forward)\s*$', line, re.I):
                continue
            # Skip very short lines at the start/end
            if len(filtered_lines) < 3 and len(line) < 10:
                continue
            filtered_lines.append(line)
        
        # Clean up the final output
        while filtered_lines and len(filtered_lines[0]) < 20:  # Remove short header lines
            filtered_lines.pop(0)
        while filtered_lines and len(filtered_lines[-1]) < 20:  # Remove short footer lines
            filtered_lines.pop()
        
        final_content = '\n'.join(filtered_lines)
        
        # Debug print
        print(f"Final content length: {len(final_content)} characters", file=sys.stderr)
        
        return final_content if final_content.strip() else None
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return None

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: extract_content.py <url>", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    content = extract_content(url)
    if content:
        print(content)  # Print the content to stdout
    else:
        print("Error: No content extracted", file=sys.stderr)
        sys.exit(1)
