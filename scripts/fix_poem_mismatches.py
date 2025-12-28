import json
import shutil
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    poems_data_path = 'Data/poems.json'
    yamato_path = 'gosanka/yamato_full.json'
    backup_path = 'gosanka/yamato_full.json.bak_fix'

    # Backup
    if not os.path.exists(backup_path):
        shutil.copy(yamato_path, backup_path)
    
    poems_data = load_json(poems_data_path)
    yamato_data = load_json(yamato_path)

    # Index poems_data by title
    poems_db = {p['title']: p for p in poems_data if 'title' in p}

    fixed_count = 0
    missing_count = 0
    
    # Iterate through yamato poems and patch
    for section in yamato_data.get('sections', []):
        for poem in section.get('poems', []):
            title = poem.get('title')
            
            if not title:
                continue
                
            if title not in poems_db:
                # print(f"Skipping '{title}' (not found in Data/poems.json)")
                missing_count += 1
                continue
            
            source = poems_db[title]
            
            # Update fields
            # We assume Data/poems.json is the source of truth for analysis
            poem['kigo'] = source.get('kigo', '')
            poem['kototama'] = source.get('kototama', '')
            
            # Map meaning -> deepening
            # Note: yamato_full uses 'deepening', poems.json uses 'meaning'
            if 'meaning' in source:
                poem['deepening'] = source['meaning']
            
            fixed_count += 1

    print(f"Fixed {fixed_count} poems.")
    print(f"Skipped {missing_count} poems not found in source.")
    
    save_json(yamato_path, yamato_data)
    print("Updates saved to gosanka/yamato_full.json")

if __name__ == '__main__':
    main()
