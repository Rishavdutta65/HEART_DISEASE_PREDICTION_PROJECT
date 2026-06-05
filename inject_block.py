import os

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'
block_path = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\help_modal_block.html'

with open(block_path, 'r', encoding='utf-8') as f:
    block_content = f.read()

for fname in ['index.html', 'reports.html', 'result.html']:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if helpModal already exists
    if 'id="helpModal"' not in content:
        if '</body>' in content:
            content = content.replace('</body>', block_content + '\n</body>', 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{fname}] Successfully injected help modal block.")
        else:
            print(f"[{fname}] ERROR: </body> tag not found!")
    else:
        print(f"[{fname}] Modal already injected.")
