
import json
import os
import re
from pathlib import Path

# Config
INDEX_FILE = 'Data/advanced_search_index.json'
DATA_DIR = 'Data'
PROJECT_ROOT = '.' 

def load_data():
    print("Loading index...")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index = json.load(f)
    return index

def load_translations():
    translations = {} # part_file -> list of items
    print("Loading translations...")
    for f in os.listdir(DATA_DIR):
        if f.startswith('teachings_translated_part') and f.endswith('.json'):
            path = os.path.join(DATA_DIR, f)
            print(f"  Loading {f}...")
            with open(path, 'r', encoding='utf-8') as fp:
                translations[f] = json.load(fp)
    return translations

def get_japanese_content(index_item, translations):
    part_file = index_item.get('part_file')
    if not part_file or part_file not in translations:
        return None
    
    item_id = index_item.get('id')
    for t_item in translations[part_file]:
        if t_item['id'] == item_id:
            return t_item.get('content')
    return None

def format_japanese_text(text):
    if not text: return ""
    
    # Aggressively strip trailing HTML tags that might break the wrapper
    # Remove </div>, </body>, </html> from the end
    cleaned = re.sub(r'(</div>|</body>|</html>)+\s*$', '', text, flags=re.IGNORECASE).strip()
    
    # Simple splitting for readability
    if '\n' in cleaned:
        return cleaned.replace('\n', '<br>')
    else:
        return cleaned.replace('。', '。<br><br>')

def resolve_path(url):
    # Try multiple convenient locations
    possibilities = [
        url,
        os.path.join('sasshi', url),
        os.path.join('search1', url),
        os.path.join('filetop', url),
        os.path.join('search1/situmon', url), # Added based on audit log
        os.path.join('search1/shi', url)
    ]
    for p in possibilities:
        if os.path.exists(p) and os.path.isfile(p):
            return p
    return None

def inject_toggle(html_path, jp_content):
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [MISSING] {html_path}")
        return False

    # Check for marker
    if '<!-- LANGUAGE TOGGLE INJECTED start -->' in content:
        # Already injected. 
        # Check if content is actually empty or broken?
        # User asked to "review all". Re-injecting is safer to ensure latest logic.
        # But we must remove the old block first to avoid duplication.
        content = re.sub(r'<!-- LANGUAGE TOGGLE INJECTED start -->.*?<!-- LANGUAGE TOGGLE INJECTED end -->\s*', '', content, flags=re.DOTALL)
        # Also clean up the hidden jp-content if it was outside the block (v1 script had it inside?)
        # v1 script had: injection = ... <div id="jp-content">...</div> ...
        # So removing the block removes the content.
        # BUT wait, the ID "jp-content" might duplicate if not careful.
        # The regex above removes the whole block.
        # print("  [UPDATE] Re-injecting...")
    
    # Target insertion point: Before <div class="translated-content">
    # If not found, try <blockquote>
    # If not found, try <div id="content"> (some generic ones)
    
    target_pattern = r'(<div class="translated-content">)'
    if not re.search(target_pattern, content):
        target_pattern = r'(<blockquote>)'
        if not re.search(target_pattern, content):
            # Fallback for pages that might use <div id="main"> or similar
            target_pattern = r'(<div id="main">|<body>)'
            # But putting it at body start might be ugly.
            # Let's stick to translated-content or blockquote for safety, 
            # or try to find Portuguese header?
            # Audit said 101 files missing. They almost certainly have "blockquote" or similar.
            pass

    if not re.search(target_pattern, content):
        print(f"  [SKIP] No target div/blockquote found in {html_path}")
        return False

    # Create Injection Block
    # We embed the JP content in a hidden div
    safe_jp = format_japanese_text(jp_content)
    
    # Updated Toggle Logic to be robust against nesting
    # We use specific IDs and try not to break layout
    
    injection = f"""
<!-- LANGUAGE TOGGLE INJECTED start -->
<div class="lang-toggle-bar" style="margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; text-align: right;">
    <button id="btn-pt" onclick="toggleLang('pt')" style="padding: 5px 10px; cursor: pointer; background: #4CAF50; color: white; border: none; border-radius: 3px;">Português</button>
    <button id="btn-jp" onclick="toggleLang('jp')" style="padding: 5px 10px; cursor: pointer; background: #ddd; color: #333; border: none; border-radius: 3px;">Original (JP)</button>
</div>

<div id="jp-content" style="display: none; font-family: 'Yu Mincho', serif; font-size: 1.1em; line-height: 1.8; background: #fff; padding: 20px; border: 1px solid #eee;">
    {safe_jp}
</div>

<script>
function toggleLang(lang) {{
    // Try to find the content container. 
    // It might be .translated-content, blockquote, or just the next sibling elements.
    // Ideally we wrap the portuguese content in a div during injection, but that parses HTML hard.
    // Instead we toggle commonly known containers.
    
    const ptSelectors = ['.translated-content', 'blockquote', '#pt-content'];
    let ptContent = null;
    
    for (let s of ptSelectors) {{
        let el = document.querySelector(s);
        if (el) {{
            ptContent = el;
            break;
        }}
    }}
    
    const jpContent = document.getElementById('jp-content');
    const btnPt = document.getElementById('btn-pt');
    const btnJp = document.getElementById('btn-jp');

    if (!ptContent && !jpContent) return;

    if (lang === 'jp') {{
        if (ptContent) ptContent.style.display = 'none';
        if (jpContent) jpContent.style.display = 'block';
        if (btnPt) {{ btnPt.style.background = '#ddd'; btnPt.style.color = '#333'; }}
        if (btnJp) {{ btnJp.style.background = '#4CAF50'; btnJp.style.color = 'white'; }}
    }} else {{
        if (ptContent) ptContent.style.display = 'block';
        if (jpContent) jpContent.style.display = 'none';
        if (btnPt) {{ btnPt.style.background = '#4CAF50'; btnPt.style.color = 'white'; }}
        if (btnJp) {{ btnJp.style.background = '#ddd'; btnJp.style.color = '#333'; }}
    }}
}}
</script>
<!-- LANGUAGE TOGGLE INJECTED end -->
"""
    
    # Inject
    # We replace the target start tag with "Injection + Target Start Tag"
    # This places the toggle bar ABOVE the content.
    new_content = re.sub(target_pattern, injection + r'\1', content, count=1)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    index = load_data()
    translations = load_translations()
    
    count = 0
    
    print("Starting Injection Process...")
    
    for item in index:
        url = item.get('url')
        if not url or not url.endswith('.html'): continue
        
        # skip if no translation available to save time finding path
        # But we need path to verify existence. 
        # Actually checking translation first is faster than IO.
        jp_text = get_japanese_content(item, translations)
        if not jp_text:
            continue

        local_path = resolve_path(url)
        if not local_path:
            # print(f"  [NOT FOUND] {url}")
            continue
        
        # Inject
        if inject_toggle(local_path, jp_text):
            count += 1
            if count % 100 == 0:
                print(f"Processed {count} files...")
        
    print(f"Finished. Successfully injected {count} files.")

if __name__ == "__main__":
    main()
