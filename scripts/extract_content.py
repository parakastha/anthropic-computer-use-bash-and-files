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
            if cls.startswith('language-'):
                language = cls[9:]
                break
            elif cls.startswith('lang-'):
                language = cls[5:]
                break
            elif cls in ['javascript', 'python', 'bash', 'json']:
                language = cls
                break
    
    code = element.get_text().strip()
    if code:
        # Clean up the code
        code = re.sub(r'\n\s*\n', '\n', code)  # Remove multiple blank lines
        code = code.strip()
        return f"```{language}\n{code}\n```"
    return ''

def process_link(element):
    href = element.get('href', '')
    text = element.get_text().strip()
    if href and text and not href.startswith(('/', '#')):  # Skip navigation links
        return f"[{text}]({href})"
    return text

def is_heading(tag):
    if not isinstance(tag, Tag) or not tag.name:
        return False
    match = re.match(r'h([1-6])', tag.name)
    return bool(match)

def get_heading_level(tag):
    match = re.match(r'h([1-6])', tag.name)
    return int(match.group(1)) if match else 0

def should_skip_element(element):
    if not isinstance(element, Tag):
        return False
    
    # Skip elements with certain classes
    classes = element.get('class', [])
    skip_classes = ['nav', 'menu', 'sidebar', 'toc', 'header', 'footer', 'navigation']
    if any(cls in skip_classes for cls in classes):
        return True
        
    # Skip elements with certain roles
    if element.get('role') in ['navigation', 'banner', 'complementary']:
        return True
        
    # Skip elements with certain IDs
    if element.get('id', '').lower() in ['nav', 'menu', 'sidebar', 'toc', 'header', 'footer']:
        return True
        
    return False

def extract_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'button']):
            element.decompose()
        
        # Find the main content area
        main = None
        for selector in [
            lambda s: s.find(class_=re.compile(r'(content|article|post|main)', re.I)),
            lambda s: s.find('main'),
            lambda s: s.find('article'),
            lambda s: s.find(attrs={'role': 'main'}),
            lambda s: s.find(id=re.compile(r'(content|article|post|main)', re.I)),
            lambda s: s  # Fallback to entire body
        ]:
            main = selector(soup)
            if main:
                break
            
        # Remove navigation elements
        for nav in main.find_all(class_=re.compile(r'nav|menu|sidebar|toc|header|footer', re.I)):
            nav.decompose()
        
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
                if text and depth <= 1:  # Only include text from top-level elements
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
        
        return '\n'.join(filtered_lines)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: extract_content.py <url>", file=sys.stderr)
        sys.exit(1)
    
    content = extract_content(sys.argv[1])
    print(content)
