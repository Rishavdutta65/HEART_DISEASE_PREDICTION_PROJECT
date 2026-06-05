import os

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'

HINT_HTML = '''                    <p class="text-slate-500 text-[10px] flex items-center gap-1.5 mb-4 select-none">
                        <i data-lucide="mouse-pointer-2" class="w-3 h-3 text-slate-600"></i>
                        Click a card to focus and read details
                    </p>\n'''

# The container div that was already added by the patch
GRID_WITH_CONTAINER = '                    <div class="medical-cards-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">'

for fname in ['index.html', 'reports.html', 'result.html']:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Click a card to focus' not in content:
        if GRID_WITH_CONTAINER in content:
            content = content.replace(
                GRID_WITH_CONTAINER,
                HINT_HTML + GRID_WITH_CONTAINER,
                1
            )
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print('[' + fname + '] Hint text injected and saved.')
        else:
            print('[' + fname + '] WARNING: Container div not found — manual check needed.')
    else:
        print('[' + fname + '] Hint text already present.')

print('\nDone.')
