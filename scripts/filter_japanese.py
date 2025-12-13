
import json
import re

INPUT_FILE = 'Data/ui_text_candidates.json'
OUTPUT_FILE = 'Data/ui_text_jp_filtered.json'

def contains_japanese(text):
    # Range for Hiragana, Katakana, and Kanji
    # Hiragana: 3040-309F
    # Katakana: 30A0-30FF
    # Kanji: 4E00-9FAF
    return re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text)

def is_mostly_japanese(text):
    # Check if a significant portion is Japanese to avoid "Page 23" type things with one symbol
    jp_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    total_chars = len(text)
    if total_chars == 0: return False
    return (jp_chars / total_chars) > 0.3 # At least 30% Japanese characters

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    filtered = {}
    
    for key in data:
        # We only care about the key (original text)
        if contains_japanese(key):
             # check if it already looks like a translation mapping?
             # existing ui_text_candidates matches key=value
             filtered[key] = "" # Empty for now, to be filled
             
    print(f"Filtered down to {len(filtered)} Japanese strings.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
