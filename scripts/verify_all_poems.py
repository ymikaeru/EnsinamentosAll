import json

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    yamato_path = 'gosanka/yamato_full.json'
    data = load_json(yamato_path)
    
    total_poems = 0
    missing_analysis = []
    
    print(f"Verifying {yamato_path}...")
    
    for section in data.get('sections', []):
        for poem in section.get('poems', []):
            total_poems += 1
            title = poem.get('title', 'Unknown Title')
            
            # Check for non-empty string fields
            kigo = poem.get('kigo', '').strip()
            kototama = poem.get('kototama', '').strip()
            deepening = poem.get('deepening', '').strip()
            
            if not kigo or not kototama or not deepening:
                missing_fields = []
                if not kigo: missing_fields.append('kigo')
                if not kototama: missing_fields.append('kototama')
                if not deepening: missing_fields.append('deepening')
                
                missing_analysis.append({
                    'title': title,
                    'missing': missing_fields
                })

    print(f"Total Poems Scanned: {total_poems}")
    print(f"Poems with Complete Analysis: {total_poems - len(missing_analysis)}")
    print(f"Poems with Missing Data: {len(missing_analysis)}")
    
    if missing_analysis:
        print("\n--- POEMS WITH MISSING DATA ---")
        for m in missing_analysis:
            print(f"- {m['title']}: Missing {', '.join(m['missing'])}")

if __name__ == '__main__':
    main()
