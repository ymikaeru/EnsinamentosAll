import json
import sys
from collections import defaultdict

print("Starting analysis...", flush=True)

file_path = '/Users/michael/Documents/Ensinamentos/Mioshie_Zenshu/gosanka/yamato_full.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sections = data.get('sections', [])
    print(f"Total sections: {len(sections)}")

    title_counts = defaultdict(int)
    empty_sections = []
    
    for i, sec in enumerate(sections):
        title = sec.get('title_pt', 'Unknown')
        poems = sec.get('poems', [])
        
        title_counts[title] += 1
        
        if not poems:
            empty_sections.append(f"Index {i}: {title} (Empty poems list)")
        elif len(poems) == 0:
             empty_sections.append(f"Index {i}: {title} (Empty poems list)")

    print("\n--- Duplicate Titles ---")
    for title, count in title_counts.items():
        if count > 1:
            print(f"'{title}': {count} occurrences")

    print("\n--- Empty Sections ---")
    if empty_sections:
        for msg in empty_sections:
            print(msg)
    else:
        print("No empty sections found.")

except Exception as e:
    print(f"Error: {e}")
