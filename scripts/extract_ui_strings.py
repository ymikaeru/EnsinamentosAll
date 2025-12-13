
import os
import json
from bs4 import BeautifulSoup
import re
import glob

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, 'Data', 'ui_text_candidates.json')

# Target directories to scan fully
SCAN_DIRS = [
    os.path.join(BASE_DIR, 'hakkousi'),
    os.path.join(BASE_DIR, 'kanren'),
    os.path.join(BASE_DIR, 'sasshi') # Appears in links in myoniti1.html
]

# Keep previous specific targets
SPECIFIC_FILES = [
    os.path.join(BASE_DIR, '2.html'),
    os.path.join(BASE_DIR, '3.html'),
]

IGNORE_EXACT_STRINGS = [
    'se', 'shiryo', 'help', 'hint', 'index', 'config', 'query',
    '3a', 'setop', '2', 'warai', 'myoniti1', 'myoniti', 'english'
]

def is_valid_candidate(text):
    if not text:
        return False
    text = text.strip()
    if not text:
        return False
    if text.isdigit():
        return False
    if re.match(r'^\d+[\-\s]*\d+$', text): return False
    # Date filters
    # Date filters removed to allow translation
    # if re.match(r'^[SGMTH]\d{1,2}[\.\/]\s*\d{1,2}[\.\/]\s*\d{1,2}$', text): return False
    # if re.match(r'^昭和\d+年.*発行$', text): return False
    
    # Filter out long content blocks (likely translated content or original japanese content)
    # Explanatory notes are usually short sentences.
    if len(text) > 300: return False
    
    if text in IGNORE_EXACT_STRINGS: return False
    
    # Filter out pure Romaji/English if we only want Japanese candidates? 
    # User wants to migrate texts. 
    return True

def process_file(soup, filename):
    strings = {}
    
    # Remove script/style
    for s in soup(['script', 'style']):
        s.decompose()
        
    # Remove blockquotes (main content)
    for bq in soup.find_all('blockquote'):
        bq.decompose()
        
    # Standard text extraction from body elements
    # focus on p, td, font, div, span
    for element in soup.find_all(['p', 'td', 'font', 'div', 'span', 'a']):
        for s in element.strings:
            s_clean = s.strip()
            if is_valid_candidate(s_clean):
                 # Filter out existing translations from previous run if needed?
                 # For now collect all candidates
                 strings[s_clean] = s_clean
                 
    return strings

def extract_strings():
    ui_strings = {}

    print("Starting candidate extraction...")
    
    all_files = SPECIFIC_FILES.copy()
    for d in SCAN_DIRS:
        if os.path.exists(d):
            all_files.extend(glob.glob(os.path.join(d, "*.html")))

    for file_path in all_files:
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
            file_strings = process_file(soup, file_path)
            ui_strings.update(file_strings)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Save to JSON
    sorted_strings = dict(sorted(ui_strings.items()))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_strings, f, indent=4, ensure_ascii=False)
    
    print(f"Extracted {len(sorted_strings)} candidates.")
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_strings()
