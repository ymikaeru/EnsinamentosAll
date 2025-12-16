#!/usr/bin/env python3
"""
Script to add showa_converter.js to all HTML files in filetop directory.
Adds the script tag just before </body> if not already present.
"""
import os
import re
from pathlib import Path

def add_script_to_html(file_path):
    """Add showa_converter.js script tag to HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if script is already added
    if 'showa_converter.js' in content:
        print(f"  [SKIP] {file_path.name} - script already present")
        return False
    
    # Find </body> and insert script before it
    script_tag = '<script src="../scripts/showa_converter.js"></script>\n'
    
    if '</body>' in content:
        new_content = content.replace('</body>', f'{script_tag}</body>')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [OK] {file_path.name} - script added")
        return True
    else:
        # No </body> tag, append at the end
        new_content = content + f'\n{script_tag}'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  [OK] {file_path.name} - script appended")
        return True

def main():
    filetop_dir = Path(__file__).parent.parent / 'filetop'
    
    print(f"Processing HTML files in: {filetop_dir}")
    print("-" * 50)
    
    count = 0
    for html_file in sorted(filetop_dir.glob('*.html')):
        if add_script_to_html(html_file):
            count += 1
    
    print("-" * 50)
    print(f"Modified {count} files.")

if __name__ == '__main__':
    main()
