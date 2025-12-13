
import json
import os
import re
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'Data', 'teachings_translated.json')

# Directories containing index files to update
INDEX_DIRS = [
    os.path.join(BASE_DIR, 'filetop'),
    os.path.join(BASE_DIR, 'hakkousi'),
    os.path.join(BASE_DIR, 'kanren'),
    # Add other directories if needed
]

def load_translations(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_title_from_md(md_text):
    if not md_text:
        return None
    
    lines = md_text.split('\n')
    for line in lines:
        stripped = line.strip()
        # Look for headers
        if stripped.startswith('#'):
            # Remove '#' characters and whitespace
            return re.sub(r'^#+\s*', '', stripped).strip()
    return None

def main():
    print(f"Loading translations from {JSON_PATH}...")
    translations = load_translations(JSON_PATH)
    
    # Create mapping: filename -> title
    file_to_title = {}
    print("Extracting titles...")
    for item in translations:
        source_file = item.get('source_file')
        content_ptbr = item.get('content_ptbr')
        
        if source_file and content_ptbr:
            title = extract_title_from_md(content_ptbr)
            if title:
                # Store by basename for easier matching
                file_to_title[source_file] = title

    print(f"Loaded {len(file_to_title)} titles.")

    # Process index files
    for index_dir in INDEX_DIRS:
        if not os.path.isdir(index_dir):
            continue
            
        print(f"Scanning directory: {index_dir}")
        for filename in os.listdir(index_dir):
            if not filename.endswith('.html'):
                continue
                
            file_path = os.path.join(index_dir, filename)
            updated = False
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                links = soup.find_all('a')
                for link in links:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Extract the filename from the href
                    # href could be "../search1/se/seiji.html"
                    href_filename = os.path.basename(href)
                    
                    if href_filename in file_to_title:
                        new_title = file_to_title[href_filename]
                        # Update link text if it's different
                        if link.string != new_title:
                            # print(f"Updating {link.string} -> {new_title} in {filename}")
                            link.string = new_title
                            updated = True
                
                if updated:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"Updated {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("Link translation complete.")

if __name__ == "__main__":
    main()
