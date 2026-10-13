import re

def fix_chart_js_colors():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The issue is that canvas (Chart.js) doesn't resolve CSS variables like 'var(--bg-card-alt)'
    # properly in all browsers, so it falls back to black. 
    # We will replace these specific CSS variables in the JS tooltip configs with 
    # dynamic checks based on the current theme.

    # Find the toggleTheme function and inject a global override for new charts
    if "const getCurrentThemeColor =" not in content:
        theme_helper = """
        const getCurrentThemeColor = (darkHex, lightHex) => document.documentElement.getAttribute('data-theme') === 'light' ? lightHex : darkHex;
        """
        # Inject the helper right before renderHistoricalChart
        content = content.replace('function renderHistoricalChart', theme_helper + '\n        function renderHistoricalChart')

    # Replace the JS string literals with the helper function calls
    replacements = {
        "'var(--bg-card-alt)'": "getCurrentThemeColor('#131D2E', '#FFFFFF')",
        "'var(--text-main)'": "getCurrentThemeColor('#E2E8F0', '#0F172A')",
        "'var(--text-muted)'": "getCurrentThemeColor('#94A3B8', '#64748B')",
        "'var(--text-dark)'": "getCurrentThemeColor('#4A5568', '#475569')",
        "'var(--border-alpha-10)'": "getCurrentThemeColor('rgba(255,255,255,0.1)', 'rgba(0,0,0,0.1)')",
        "'var(--bg-page)'": "getCurrentThemeColor('#0A0F1E', '#F8FAFC')"
    }

    # Only apply these replacements to the JavaScript section (after </style>)
    parts = content.split('</style>')
    if len(parts) == 2:
        head = parts[0]
        body = parts[1]
        
        # We only want to replace inside the Chart configurations, which are in the script tags.
        # But we can just safely replace them everywhere in the body since it's JS.
        # Wait, if we replace them in JS strings, what if they are inside HTML template literals?
        # Let's be very specific and target only tooltip and legend configurations.
        
        for old, new in replacements.items():
            # Specifically target lines with 'tooltip:' or 'backgroundColor:' or 'titleColor:' or 'bodyColor:' or 'color:'
            # A safer regex approach:
            body = re.sub(r'backgroundColor:\s*' + re.escape(old), f'backgroundColor: {new}', body)
            body = re.sub(r'titleColor:\s*' + re.escape(old), f'titleColor: {new}', body)
            body = re.sub(r'bodyColor:\s*' + re.escape(old), f'bodyColor: {new}', body)
            body = re.sub(r'color:\s*' + re.escape(old), f'color: {new}', body)
            body = re.sub(r'borderColor:\s*' + re.escape(old), f'borderColor: {new}', body)
            
        content = head + '</style>' + body

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Chart.js tooltip colors successfully patched!")

if __name__ == '__main__':
    fix_chart_js_colors()
