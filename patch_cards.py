import os
import re

BASE = r'e:\APP E TEASER\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\HEART_DISEASE_PROJECT\frontend\templates'

# ─── CSS injected before closing </style> ────────────────────────────────────
CARD_CSS = """
        /* === Medical Card Focus Interaction === */
        .medical-card {
            cursor: pointer;
            transform: scale(1);
            transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1),
                        box-shadow 0.35s ease,
                        opacity 0.35s ease,
                        border-color 0.35s ease;
            position: relative;
            z-index: 1;
        }
        .medical-card.active-card {
            transform: scale(1.07);
            z-index: 20;
            box-shadow: 0 0 0 2px rgba(99, 202, 255, 0.50),
                        0 8px 45px rgba(99, 202, 255, 0.22),
                        0 0 70px rgba(99, 202, 255, 0.10);
        }
        .medical-cards-container.has-active .medical-card:not(.active-card) {
            opacity: 0.35;
            transform: scale(0.97);
        }
        @media (max-width: 768px) {
            .medical-card.active-card {
                transform: scale(1.04);
            }
        }
"""

# ─── Hint text HTML injected just before the card grid ───────────────────────
HINT_HTML = """                    <p class="text-slate-500 text-[10px] flex items-center gap-1.5 mb-4 select-none">
                        <i data-lucide="mouse-pointer-2" class="w-3 h-3 text-slate-600"></i>
                        Click a card to focus and read details
                    </p>
"""

# ─── JS function injected before filterMedicalFields ─────────────────────────
FOCUS_JS = """
        // === Medical Card Focus / Zoom Interaction ===
        function focusMedicalCard(card) {
            var container = document.querySelector('.medical-cards-container');
            if (!container) return;
            var isActive = card.classList.contains('active-card');
            document.querySelectorAll('.medical-card').forEach(function(c) {
                c.classList.remove('active-card');
            });
            container.classList.remove('has-active');
            if (!isActive) {
                card.classList.add('active-card');
                container.classList.add('has-active');
                // Smooth scroll card into view on mobile without breaking desktop layout
                if (window.innerWidth < 768) {
                    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        }

"""

GRID_OLD = '                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">'
GRID_NEW = HINT_HTML + '                    <div class="medical-cards-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">'

files = ['index.html', 'reports.html', 'result.html']

for fname in files:
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Inject CSS before the first </style>
    if '/* === Medical Card Focus Interaction ===' not in content:
        content = content.replace('</style>', CARD_CSS + '    </style>', 1)
        changed = True
        print(f'[{fname}] CSS injected.')

    # 2. Add onclick="focusMedicalCard(this)" to every medical-card div
    if 'focusMedicalCard(this)' not in content:
        content = re.sub(
            r'(<div\s)(class="medical-card )',
            r'\1onclick="focusMedicalCard(this)" \2',
            content
        )
        changed = True
        print(f'[{fname}] onclick handlers added.')

    # 3. Replace the card grid div with container-classed + hint text
    if 'medical-cards-container' not in content:
        content = content.replace(GRID_OLD, GRID_NEW, 1)
        changed = True
        print(f'[{fname}] Hint text + container class added.')

    # 4. Inject focusMedicalCard JS function before filterMedicalFields
    if 'function focusMedicalCard' not in content:
        content = content.replace(
            '        function filterMedicalFields() {',
            FOCUS_JS + '        function filterMedicalFields() {',
            1
        )
        changed = True
        print(f'[{fname}] focusMedicalCard JS injected.')

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[{fname}] Saved.')
    else:
        print(f'[{fname}] Already up to date — no changes needed.')

print('\nAll done.')
