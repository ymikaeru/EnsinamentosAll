import json
import difflib

def normalize_text(text):
    if not text:
        return ""
    return text.strip().replace('\n', ' ').replace('\r', '')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    poems_data_path = 'Data/poems.json'
    yamato_path = 'gosanka/yamato_full.json'

    poems_data = load_json(poems_data_path)
    # poems_data is a list of dicts

    yamato_data = load_json(yamato_path)
    # yamato_data has 'sections' -> 'poems'

    # Flatten yamato poems
    yamato_poems = []
    for section in yamato_data.get('sections', []):
        for poem in section.get('poems', []):
            yamato_poems.append(poem)

    # Index poems_data by title for easy lookup
    poems_db = {p['title']: p for p in poems_data if 'title' in p}

    mismatches = []

    print(f"Checking {len(yamato_poems)} poems from yamato_full.json against Data/poems.json...")

    for y_poem in yamato_poems:
        title = y_poem.get('title')
        if not title:
            continue
        
        if title not in poems_db:
            print(f"Warning: Title '{title}' not found in Data/poems.json")
            continue

        d_poem = poems_db[title]

        # Check Kigo
        y_kigo = normalize_text(y_poem.get('kigo', ''))
        d_kigo = normalize_text(d_poem.get('kigo', ''))

        # Simple check: are they roughly the same length or identical?
        # If one talks about "sea" and the other "mountain", that's a mismatch.
        # We can use SequenceMatcher
        ratio = difflib.SequenceMatcher(None, y_kigo, d_kigo).ratio()

        if ratio < 0.5: # Arbitrary threshold, but if they are completely different text it will be low
            mismatches.append({
                'title': title,
                'field': 'kigo',
                'yamato_val': y_kigo,
                'data_val': d_kigo,
                'ratio': ratio
            })

    print(f"\nFound {len(mismatches)} mismatches.")
    
    # Print distinct titles with mismatches
    mismatched_titles = set(m['title'] for m in mismatches)
    print(f"Affected Poems ({len(mismatched_titles)}):")
    for t in mismatched_titles:
        print(f"- {t}")

    # Detailed dump for the first few
    print("\n--- DETAILED EXAMPLES ---")
    for m in mismatches[:5]:
        print(f"\n[{m['title']}] - {m['field']} (Match Ratio: {m['ratio']:.2f})")
        print(f"YAMATO (Current): {m['yamato_val'][:100]}...")
        print(f"DATA (Correct):   {m['data_val'][:100]}...")

if __name__ == '__main__':
    main()
