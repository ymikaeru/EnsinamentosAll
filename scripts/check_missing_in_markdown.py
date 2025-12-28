import json
import re

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_text(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def main():
    poems_data_path = 'Data/poems.json'
    yamato_path = 'gosanka/yamato_full.json'
    markdown_path = 'Data/Yama To Mizu _ Traducao Completo Aprofundado.md'

    poems_data = load_json(poems_data_path)
    # db of existing titles
    poems_db = {p['title']: True for p in poems_data if 'title' in p}

    yamato_data = load_json(yamato_path)
    
    missing_titles = []
    
    # Identify missing poems again
    for section in yamato_data.get('sections', []):
        for poem in section.get('poems', []):
            title = poem.get('title')
            if title and title not in poems_db:
                missing_titles.append(title)

    missing_titles = sorted(list(set(missing_titles))) # distinct items

    markdown_content = load_text(markdown_path)
    
    found_in_markdown = []
    not_found_in_markdown = []

    print(f"Checking {len(missing_titles)} missing poems against '{markdown_path}'...\n")

    for title in missing_titles:
        # Check if title exists in markdown
        # We look for "## [Number]. [Title]" or just the title string
        if title in markdown_content:
            found_in_markdown.append(title)
        else:
            not_found_in_markdown.append(title)

    print(f"Found {len(found_in_markdown)} poems in markdown.")
    print(f"Still missing {len(not_found_in_markdown)} poems.")
    
    if len(found_in_markdown) > 0:
        print("\nExamples found:")
        for t in found_in_markdown[:10]:
            print(f"- {t}")

    if len(found_in_markdown) > 0:
        print("\nAll Found:")
        for t in found_in_markdown:
             print(f"[FOUND] {t}")

    if len(not_found_in_markdown) > 0:
        print("\nNot Found in Markdown:")
        for t in not_found_in_markdown:
            print(f"[MISSING] {t}")

if __name__ == '__main__':
    main()
