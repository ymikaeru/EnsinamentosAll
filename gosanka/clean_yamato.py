import json
import shutil
import os

file_path = '/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu/gosanka/yamato_full.json'
backup_path = file_path + '.backup'

print("Starting cleanup...", flush=True)

try:
    # 1. Create Backup
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"Backup created at {backup_path}")

    # 2. Load Data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sections = data.get('sections', [])
    initial_count = len(sections)
    print(f"Initial sections: {initial_count}")

    # 3. Filter Sections
    # Keep sections that have 'poems' and the list is not empty
    cleaned_sections = [
        sec for sec in sections 
        if sec.get('poems') and len(sec['poems']) > 0
    ]

    final_count = len(cleaned_sections)
    removed_count = initial_count - final_count

    print(f"Final sections: {final_count}")
    print(f"Removed sections: {removed_count}")

    # 4. Save Data
    data['sections'] = cleaned_sections
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print("Cleanup complete. Saved updated file.")

except Exception as e:
    print(f"Error during cleanup: {e}")
