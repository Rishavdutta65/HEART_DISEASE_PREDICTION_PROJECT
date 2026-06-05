import os

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'

for fname in ['index.html', 'reports.html', 'result.html']:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\n=== {fname} matches ===")
    for idx, line in enumerate(lines):
        if 'medical-card' in line and 'class=' in line:
            print(f"  Line {idx+1}: {repr(line)}")
            # print the parent container if possible (i.e. previous line)
            print(f"    Prev: {repr(lines[idx-1])}")
            break
