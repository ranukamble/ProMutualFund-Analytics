import re

def apply_theme_variables():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements for hardcoded colors to use CSS variables
    replacements = {
        '#131D2E': 'var(--bg-card-alt)',
        '#0D1B2A': 'var(--bg-card)',
        '#0A0F1E': 'var(--bg-page)',
        '#E2E8F0': 'var(--text-main)',
        '#94A3B8': 'var(--text-muted)',
        '#4A5568': 'var(--text-dark)',
        'rgba(255,255,255,0.03)': 'var(--border-alpha-3)',
        'rgba(255,255,255,0.04)': 'var(--border-alpha-4)',
        'rgba(255,255,255,0.05)': 'var(--border-alpha-5)',
        'rgba(255,255,255,0.06)': 'var(--border-alpha-6)',
        'rgba(255,255,255,0.08)': 'var(--border-alpha-8)',
        'rgba(255,255,255,0.1)': 'var(--border-alpha-10)',
        'rgba(0,0,0,0.2)': 'var(--shadow-alpha)',
        'rgba(255,255,255,0.02)': 'var(--hover-alpha)',
    }

    # Don't replace inside the :root definition itself
    parts = content.split('/* Layout */')
    if len(parts) == 2:
        head = parts[0]
        body = parts[1]
        for old, new in replacements.items():
            body = body.replace(old, new)
        content = head + '/* Layout */' + body

    # Inject the light theme CSS variables
    theme_css = """
        :root {
            --bg-page: #0A0F1E; --bg-panel: #0D1520; --bg-card: #0D1B2A; --bg-card-alt: #131D2E;
            --border-color: rgba(255,255,255,0.06); --border-light: rgba(255,255,255,0.08);
            --border-alpha-3: rgba(255,255,255,0.03); --border-alpha-4: rgba(255,255,255,0.04);
            --border-alpha-5: rgba(255,255,255,0.05); --border-alpha-6: rgba(255,255,255,0.06);
            --border-alpha-8: rgba(255,255,255,0.08); --border-alpha-10: rgba(255,255,255,0.1);
            --shadow-alpha: rgba(0,0,0,0.2); --hover-alpha: rgba(255,255,255,0.02);
            --text-main: #F1F5F9; --text-muted: #94A3B8; --text-dark: #4A5568;
            --cyan: #00D2FF; --cyan-light: #67E8F9; --blue: #3A7BD5; --green: #34D399;
            --red: #F87171; --purple: #8B5CF6; --purple-light: #A78BFA; --orange: #F59E0B;
            --invert-logo: 0;
        }
        
        [data-theme="light"] {
            --bg-page: #F8FAFC; --bg-panel: #F1F5F9; --bg-card: #FFFFFF; --bg-card-alt: #F8FAFC;
            --border-color: rgba(0,0,0,0.1); --border-light: rgba(0,0,0,0.15);
            --border-alpha-3: rgba(0,0,0,0.03); --border-alpha-4: rgba(0,0,0,0.04);
            --border-alpha-5: rgba(0,0,0,0.05); --border-alpha-6: rgba(0,0,0,0.06);
            --border-alpha-8: rgba(0,0,0,0.08); --border-alpha-10: rgba(0,0,0,0.1);
            --shadow-alpha: rgba(0,0,0,0.05); --hover-alpha: rgba(0,0,0,0.03);
            --text-main: #0F172A; --text-muted: #475569; --text-dark: #94A3B8;
            --invert-logo: 1;
        }
        
        [data-theme="light"] .header {
            background: linear-gradient(135deg, #FFFFFF, #F1F5F9) !important;
        }
        [data-theme="light"] .header-ticker {
            background: rgba(0,0,0,0.05) !important;
        }
        [data-theme="light"] .header-ticker::before {
            background: linear-gradient(90deg, #FFFFFF, transparent) !important;
        }
        [data-theme="light"] .header-ticker::after {
            background: linear-gradient(-90deg, #FFFFFF, transparent) !important;
        }
        [data-theme="light"] .shimmer {
            background: linear-gradient(90deg, #F8FAFC 0%, #E2E8F0 50%, #F8FAFC 100%) !important;
        }
        [data-theme="light"] .header-logo {
            filter: invert(var(--invert-logo)) hue-rotate(180deg) !important;
        }
        [data-theme="light"] #pgSearchResults {
            background: var(--bg-page) !important;
        }
        [data-theme="light"] select, [data-theme="light"] input {
            color: #0F172A !important;
        }
        
        /* Force color fixes */
        [data-theme="light"] .header-title-wrap h1 { color: #0F172A !important; }
"""
    # Replace old root with new one
    content = re.sub(r':root\s*\{[^}]+\}', theme_css, content, count=1)

    # Add the theme toggle button HTML
    theme_btn = """<button onclick="toggleTheme()" id="themeToggleBtn" style="background: rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.2); color: var(--text-main); font-size: 16px; cursor: pointer; width: 36px; height: 36px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; justify-content: center;" title="Toggle Theme">🌙</button>
            <button class="toggle-sidebar-btn" """
    content = content.replace('<button class="toggle-sidebar-btn" ', theme_btn)

    # Add the JS toggle logic
    js_logic = """
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            document.getElementById('themeToggleBtn').textContent = newTheme === 'light' ? '☀️' : '🌙';
            
            // Fix Chart.js tooltip background and grid lines
            if (typeof Chart !== 'undefined') {
                Chart.helpers.each(Chart.instances, function(instance){
                    if (instance.options.plugins && instance.options.plugins.tooltip) {
                        instance.options.plugins.tooltip.backgroundColor = newTheme === 'light' ? '#FFFFFF' : '#131D2E';
                        instance.options.plugins.tooltip.titleColor = newTheme === 'light' ? '#0F172A' : '#64748B';
                        instance.options.plugins.tooltip.bodyColor = newTheme === 'light' ? '#475569' : '#E2E8F0';
                    }
                    if (instance.options.scales) {
                        if (instance.options.scales.x && instance.options.scales.x.grid) {
                            instance.options.scales.x.grid.color = newTheme === 'light' ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.03)';
                        }
                        if (instance.options.scales.y && instance.options.scales.y.grid) {
                            instance.options.scales.y.grid.color = newTheme === 'light' ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.03)';
                        }
                    }
                    instance.update();
                });
            }
        }
        
        // On load
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            if (savedTheme === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
                const btn = document.getElementById('themeToggleBtn');
                if (btn) btn.textContent = '☀️';
            }
        });
    </script>
</body>"""
    
    content = content.replace('</script>\n</body>', js_logic)

    # Add header-logo class to the image
    content = content.replace('<img src="/static/logo.png"', '<img src="/static/logo.png" class="header-logo"')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Theme successfully patched!")

if __name__ == '__main__':
    apply_theme_variables()
