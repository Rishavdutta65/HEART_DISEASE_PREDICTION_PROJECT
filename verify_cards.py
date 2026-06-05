import os

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'

for fname in ['index.html', 'reports.html', 'result.html']:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'CSS active-card':      '/* === Medical Card Focus Interaction ===' in content,
        'onclick handler':      'focusMedicalCard(this)' in content,
        'JS function':          'function focusMedicalCard' in content,
        'container class':      'medical-cards-container' in content,
        'hint text':            'Click a card to focus' in content,
        'has-active scoping':   'has-active' in content,
    }

    print('\n=== ' + fname + ' ===')
    for k, v in checks.items():
        status = 'OK' if v else 'MISSING'
        print('  [' + status + '] ' + k)

print('\nDone.')
