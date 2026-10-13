import re

def fix_portfolio_overview_light_mode():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    css_fixes = """
        /* Professional Portfolio Overview Light Mode Fixes */
        [data-theme="light"] #pg_professional_overview {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-light) !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.05) !important;
        }
        
        [data-theme="light"] #pg_professional_overview > div > div {
            background: var(--bg-card-alt) !important;
            border: 1px solid var(--border-light) !important;
        }
        
        /* Make the purple/cyan accents darker for readability on white background */
        [data-theme="light"] #pg_professional_overview [style*="color:#00D2FF"],
        [data-theme="light"] #pg_professional_overview [style*="color: #00D2FF"] {
            color: #0284C7 !important;
        }
        
        [data-theme="light"] #pg_professional_overview [style*="color:#A78BFA"],
        [data-theme="light"] #pg_professional_overview [style*="color: #A78BFA"] {
            color: #7C3AED !important;
        }
        
        /* Fix the h3 title color */
        [data-theme="light"] #pg_professional_overview h3 {
            color: var(--text-main) !important;
        }
    """

    if "Professional Portfolio Overview Light Mode Fixes" not in content:
        # Inject right before </style>
        content = content.replace('</style>', css_fixes + '\n    </style>')
    else:
        # If it was already injected, let's replace the old block with the new one
        content = re.sub(r'/\* Professional Portfolio Overview Light Mode Fixes \*/.*?(?=\s*</style>)', css_fixes.strip(), content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Professional Portfolio Overview light mode successfully patched!")

if __name__ == '__main__':
    fix_portfolio_overview_light_mode()
