
import os
import re

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    print(f"Scanning {BASE_DIR} for image path replacements...")
    
    count = 0
    # Targets: absolute URL found in grep, and the user's requested pattern
    replacements = [
        ('http://rattail.verse.jp/photo/', '../img/'),
        ('src="../../photo/', 'src="../img/'),
        ('src="../../Photo/', 'src="../img/')
    ]
    
    for root, dirs, files in os.walk(BASE_DIR):
        for filename in files:
            if not filename.endswith('.html'):
                continue
                
            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                
                for target, replacement in replacements:
                    if target in content:
                        content = content.replace(target, replacement)
                        
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    print(f"Updated {filename}")
                    count += 1
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"Finished. Updated {count} files.")

if __name__ == "__main__":
    main()
