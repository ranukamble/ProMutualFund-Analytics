import re

def fix_light_mode_text():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    css_fixes = """
        /* Comprehensive Light Mode Text Fixes */
        [data-theme="light"] .hero-title,
        [data-theme="light"] h1:not([style*="color"]), 
        [data-theme="light"] h2:not([style*="color"]), 
        [data-theme="light"] h3:not([style*="color"]), 
        [data-theme="light"] h4:not([style*="color"]):not(.text-green):not(.text-red),
        [data-theme="light"] .stat-val-huge,
        [data-theme="light"] #savedPortfolioTitle,
        [data-theme="light"] #savedTotalInv,
        [data-theme="light"] #pbTotalAlloc,
        [data-theme="light"] #pbDonutCenter,
        [data-theme="light"] .c-stat-box h4:not([style*="color"]):not(.text-green):not(.text-red),
        [data-theme="light"] .chart-title,
        [data-theme="light"] .drawer-header h2,
        [data-theme="light"] .ticker-item,
        [data-theme="light"] .qstat-val:not(.text-green):not(.text-red),
        [data-theme="light"] #val-exit {
            color: var(--text-main) !important;
        }
        
        [data-theme="light"] .stat-label,
        [data-theme="light"] .stat-sub,
        [data-theme="light"] .chart-sub,
        [data-theme="light"] .c-stat-box p,
        [data-theme="light"] .hero-label,
        [data-theme="light"] .t-badge {
            color: var(--text-muted) !important;
        }
        
        /* Ensure table text inside elements gets correct color */
        [data-theme="light"] #pgSelectedFunds > div > div > div {
            color: var(--text-main) !important;
        }
        
        [data-theme="light"] #pgSelectedFunds > div > div[style*="font-size:10px"] {
            color: var(--text-muted) !important;
        }

        /* Ensure standard text elements inside cards aren't white */
        [data-theme="light"] .text-white,
        [data-theme="light"] span[style*="color: white"],
        [data-theme="light"] span[style*="color:white"],
        [data-theme="light"] span[style*="color: #FFF"],
        [data-theme="light"] span[style*="color:#FFF"],
        [data-theme="light"] span[style*="color: #F1F5F9"],
        [data-theme="light"] span[style*="color:#F1F5F9"],
        [data-theme="light"] div[style*="color: #cbd5e1"],
        [data-theme="light"] div[style*="color:#cbd5e1"],
        [data-theme="light"] span[style*="color: #CBD5E1"],
        [data-theme="light"] span[style*="color:#CBD5E1"] {
            color: var(--text-main) !important;
        }
        
        /* Preserve button text colors (they have gradient backgrounds so they need to stay white) */
        [data-theme="light"] button[style*="color: white"],
        [data-theme="light"] button[style*="color:white"],
        [data-theme="light"] button[style*="color: #FFF"],
        [data-theme="light"] button[style*="color:#FFF"] {
            color: white !important;
        }
        
        /* Protect specific green/red text globally */
        [data-theme="light"] .text-green { color: #10B981 !important; }
        [data-theme="light"] .text-red { color: #EF4444 !important; }
        
        /* Fix the hamburger icon so it turns black in light mode */
        [data-theme="light"] .toggle-sidebar-btn {
            color: var(--text-main) !important;
        }
    """

    if "Comprehensive Light Mode Text Fixes" not in content:
        # Inject right before </style>
        content = content.replace('</style>', css_fixes + '\n    </style>')
    else:
        # If it was already injected, let's replace the old block with the new one
        content = re.sub(r'/\* Comprehensive Light Mode Text Fixes \*/.*?(?=\s*</style>)', css_fixes.strip(), content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Light mode text colors patched (Restored Semantic Chart Colors)!")

if __name__ == '__main__':
    fix_light_mode_text()
