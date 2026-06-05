import os

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'

HINT_HTML = """                    <p class="text-slate-500 text-[10px] flex items-center gap-1.5 mb-4 select-none">
                        <i data-lucide="mouse-pointer-2" class="w-3 h-3 text-slate-600"></i>
                        Click a card to focus and read details
                    </p>
"""

GRID_NEW = '                    <div class="medical-cards-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">'

for fname in ['index.html', 'reports.html', 'result.html']:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Locate line with '<!-- 1. Age'
    age_idx = -1
    for idx, line in enumerate(lines):
        if '<!-- 1. Age' in line:
            age_idx = idx
            break
            
    if age_idx == -1:
        print(f"[{fname}] Could not find age card comment!")
        continue
        
    # Search upwards for the closest grid div
    grid_idx = -1
    for idx in range(age_idx - 1, -1, -1):
        if 'grid grid-cols-1' in lines[idx]:
            grid_idx = idx
            break
            
    if grid_idx == -1:
        print(f"[{fname}] Could not find grid container before age card!")
        continue
        
    original_line = lines[grid_idx]
    print(f"[{fname}] Found grid container line at {grid_idx+1}: {repr(original_line)}")
    
    # Replace the line
    lines[grid_idx] = HINT_HTML + GRID_NEW + '\n'
    
    # Save the file
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"[{fname}] Successfully added hint text and medical-cards-container class.")
