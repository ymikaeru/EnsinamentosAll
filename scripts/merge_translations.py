
import json
import os

MAIN_FILE = 'Data/ui_text_pt.json'
SUPPLEMENTAL_FILE = 'Data/ui_text_pt_supplemental.json'

def main():
    if not os.path.exists(MAIN_FILE) or not os.path.exists(SUPPLEMENTAL_FILE):
        print("One of the input files is missing.")
        return

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        main_data = json.load(f)
        
    with open(SUPPLEMENTAL_FILE, 'r', encoding='utf-8') as f:
        supp_data = json.load(f)
        
    # Update main with supplemental (supplemental takes precedence if conflict, or add new)
    main_data.update(supp_data)
    
    print(f"Merged {len(supp_data)} supplemental items. Total items: {len(main_data)}")
    
    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
