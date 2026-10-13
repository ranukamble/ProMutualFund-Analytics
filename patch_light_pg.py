import re

def fix_portfolio_generator_light_mode():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    css_fixes = """
        /* Portfolio Generator Light Mode Fixes */
        [data-theme="light"] #pgCol2 {
            background: var(--bg-page) !important;
        }
        
        [data-theme="light"] #pgTopBar {
            background: rgba(248, 250, 252, 0.85) !important;
            border-bottom: 1px solid var(--border-light) !important;
        }
        
        [data-theme="light"] [style*="background:rgba(10,15,30,0.9)"],
        [data-theme="light"] [style*="background: rgba(10,15,30,0.9)"] {
            background: rgba(255, 255, 255, 0.9) !important;
            border-top: 1px solid var(--border-light) !important;
        }
        
        /* Ensure specific puzzle/empty state text is visible */
        [data-theme="light"] #pgEmptyState h2 {
            color: var(--text-main) !important;
        }
        [data-theme="light"] #pgEmptyState p {
            color: var(--text-muted) !important;
        }
    """

    if "Portfolio Generator Light Mode Fixes" not in content:
        # Inject right before </style>
        content = content.replace('</style>', css_fixes + '\n    </style>')
    else:
        # If it was already injected, let's replace the old block with the new one
        content = re.sub(r'/\* Portfolio Generator Light Mode Fixes \*/.*?(?=\s*</style>)', css_fixes.strip(), content, flags=re.DOTALL)

    # Let's also do a quick sweep and replace any inline #060A10 with var(--bg-page)
    # just in case it's used elsewhere as a background.
    # Note: We won't do a full text replacement to avoid breaking HTML structure,
    # relying on the CSS override is safer, but replacing the string is also okay.
    content = content.replace('background:#060A10', 'background:var(--bg-page)')
    content = content.replace('background: #060A10', 'background: var(--bg-page)')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Portfolio Generator light mode successfully patched!")

if __name__ == '__main__':
    fix_portfolio_generator_light_mode()
