import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    poems_data_path = 'Data/poems.json'
    yamato_path = 'gosanka/yamato_full.json'

    poems_data = load_json(poems_data_path)
    # db of existing titles
    poems_db = {p['title']: True for p in poems_data if 'title' in p}

    yamato_data = load_json(yamato_path)
    
    missing_titles = []

    for section in yamato_data.get('sections', []):
        for poem in section.get('poems', []):
            title = poem.get('title')
            if title and title not in poems_db:
                missing_titles.append(title)

    print(f"Found {len(missing_titles)} poems in yamato_full.json that are NOT in Data/poems.json:\n")
    for i, title in enumerate(missing_titles, 1):
        print(f"{i}. {title}")

if __name__ == '__main__':
    main()
