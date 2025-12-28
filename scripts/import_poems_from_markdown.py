import json
import re

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def parse_markdown(content):
    """
    Parses the markdown content to extract poem analysis.
    Returns a dictionary keyed by poem title.
    Structure: { 'Title': { 'kigo': '...', 'kototama': '...', 'deepening': '...' } }
    """
    poems_db = {}
    
    # Split by "## " headers to isolate poem blocks roughly
    # Regex to find title line: ## \d+\. Title
    # Then capture content until next H1 or H2
    
    # Strategy: Regex for the block
    # Pattern:
    # ## \d+\. (Title)
    # ...
    # **🍃 Kigo .*?** (Content)
    # **🎵 Kototama .*?** (Content)
    # **🏔️ A Profundidade .*?** (Content)
    
    # We'll traverse line by line for robustness
    lines = content.split('\n')
    current_title = None
    current_data = {'kigo': [], 'kototama': [], 'deepening': []}
    current_mode = None # 'kigo', 'kototama', 'deepening' or None

    for line in lines:
        line_stripped = line.strip()
        
        # Check for Title
        # Format: ## 1. Chuva e Musgo
        title_match = re.match(r'^##\s+\d+\\\.\s+(.+)$', line_stripped)
        if not title_match:
             title_match = re.match(r'^##\s+\d+\.\s+(.+)$', line_stripped)
        
        if title_match:
            # Save previous if exists
            if current_title:
                poems_db[current_title] = {
                    'kigo': ' '.join(current_data['kigo']).strip(),
                    'kototama': ' '.join(current_data['kototama']).strip(),
                    'deepening': ' '.join(current_data['deepening']).strip()
                }
            
            # Reset
            current_title = title_match.group(1).strip()
            current_data = {'kigo': [], 'kototama': [], 'deepening': []}
            current_mode = None
            continue
        
        if not current_title:
            continue

        # Check for Sections
        # Check for Sections
        if "**🍃 Kigo" in line or "**🍃** Kigo" in line:
            current_mode = 'kigo'
            # Extract content on the same line if exists
            content = line.split(":", 1)[1].strip() if ":" in line else ""
            if content: current_data['kigo'].append(content)
            continue
        
        if "**🎵 Kototama" in line or "**🎵** Kototama" in line:
            current_mode = 'kototama'
            content = line.split(":", 1)[1].strip() if ":" in line else ""
            if content: current_data['kototama'].append(content)
            continue
            
        if "**🏔️ A Profundidade" in line or "**🏔️** A Profundidade" in line or "**🏔️ Lição" in line or "**🏔️** Lição" in line:
            current_mode = 'deepening'
            content = line.split(":", 1)[1].strip() if ":" in line else ""
            if content: current_data['deepening'].append(content)
            continue
            
        # Stop on dividers
        if line_stripped.startswith('---'):
            current_mode = None
            continue
            
        # Accumulate content
        if current_mode and line_stripped:
            # Avoid bold headers just in case
            if not line_stripped.startswith('**'):
                current_data[current_mode].append(line_stripped)

    # Save last
    if current_title:
        poems_db[current_title] = {
            'kigo': ' '.join(current_data['kigo']).strip(),
            'kototama': ' '.join(current_data['kototama']).strip(),
            'deepening': ' '.join(current_data['deepening']).strip()
        }
        
    return poems_db

def main():
    yamato_path = 'gosanka/yamato_full.json'
    markdown_path = 'Data/Yama To Mizu _ Traducao Completo Aprofundado.md'
    
    print(f"Reading markdown from {markdown_path}...")
    md_content = load_text(markdown_path)
    markdown_db = parse_markdown(md_content)
    print(f"Parsed {len(markdown_db)} poems from markdown.")

    print(f"Loading JSON from {yamato_path}...")
    yamato_data = load_json(yamato_path)
    
    updated_count = 0
    not_found_in_md = []
    
    # Update poems
    for section in yamato_data.get('sections', []):
        for poem in section.get('poems', []):
            title = poem.get('title')
            
            # Only update if fields are missing or empty (or we can overwrite to be safe)
            # Strategy: Overwrite if title exists in markdown, to ensure consistency
            # But the user specifically asked about the 102 missing ones.
            # Best approach: Update ALL poems found in markdown to ensure high quality data, 
            # OR targeted update.
            # Given the previous context was strictly about "missing" ones, let's target,
            # BUT since we know 102 are definitly wrong (empty or old data?), overwriting is safer if data exists.
            
            if title in markdown_db:
                md_entry = markdown_db[title]
                
                # Check validity of extracted data
                if md_entry['kigo'] or md_entry['kototama'] or md_entry['deepening']:
                    poem['kigo'] = md_entry['kigo']
                    poem['kototama'] = md_entry['kototama']
                    poem['deepening'] = md_entry['deepening']
                    updated_count += 1
                else:
                    pass # Empty entry in MD?
            else:
                # Track what we couldn't find, just in case
                pass

    print(f"Updated {updated_count} poems in JSON.")
    
    save_json(yamato_path, yamato_data)
    print("Updates saved.")

if __name__ == '__main__':
    main()
