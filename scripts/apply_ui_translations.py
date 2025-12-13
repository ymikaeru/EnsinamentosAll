
import os
import json
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATION_FILE = os.path.join(BASE_DIR, 'Data', 'ui_text_pt.json')

# Target files to scan
TARGET_DIRS = [
    BASE_DIR, # Root (2.html, 3.html)
    os.path.join(BASE_DIR, 'filetop'),
    os.path.join(BASE_DIR, 'hakkousi'),
    os.path.join(BASE_DIR, 'kanren'),
     os.path.join(BASE_DIR, 'search1'), # Also scan content files for header/footer translation
     # search2? os.path.join(BASE_DIR, 'search2'), 
]

def load_translations():
    with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    if not os.path.exists(TRANSLATION_FILE):
        print("Translation file not found.")
        return

    translations = load_translations()
    # Sort keys by length descending to avoid partial replacement issues if any
    sorted_keys = sorted(translations.keys(), key=len, reverse=True)
    
    print("Starting translation application...")
    
    count = 0
    
    for target_dir in TARGET_DIRS:
        if not os.path.isdir(target_dir):
            continue
            
        for filename in os.listdir(target_dir):
            if not filename.endswith('.html'):
                continue
                
            file_path = os.path.join(target_dir, filename)
            updated = False
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Approach: String replacement on the whole content is risky but effective for exact matches
                # BeautifulSoup parsing is safer but might alter formatting.
                # Given strict exact matches from extraction, string replacement is viable if keys are unique enough.
                # However, keys like "1", "2" (if extracted) would be dangerous.
                # But our extraction filtered numbers.
                # "あ" -> "A". This is safe in UI context but dangerous in text?
                # "あ" only appears in navigation tables usually.
                # Let's try BeautifulSoup to be safer and target text nodes.

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                # Replace text in text nodes
                for element in soup.find_all(string=True):
                    # Skip if parent is script or style
                    if element.parent.name in ['script', 'style']:
                        continue
                        
                    # Skip blockquotes (content)
                    if element.find_parent('blockquote'):
                        continue

                    text = element.string
                    if not text:
                        continue
                        
                    clean_text = text.strip()
                    if clean_text in translations:
                        new_text = translations[clean_text]
                        # Preserve whitespace if possible, or just replace
                        # if strict match:
                        if text == clean_text:
                            element.replace_with(new_text)
                            updated = True
                        else:
                            # Text has surrounding whitespace
                            # Replace the clean part
                            new_content = text.replace(clean_text, new_text)
                            element.replace_with(new_content)
                            updated = True

                # Specific handling for Input values
                for input_tag in soup.find_all('input'):
                     val = input_tag.get('value')
                     if val and val.strip() in translations:
                         input_tag['value'] = translations[val.strip()]
                         updated = True

                if updated:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"Updated {filename}")
                    count += 1
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"Translation complete. Updated {count} files.")

if __name__ == "__main__":
    main()
