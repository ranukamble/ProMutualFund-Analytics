import re
import sys
import tempfile
import subprocess
import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'HTML_TEMPLATE\s*=\s*\"\"\"(.*)\"\"\"', content, re.DOTALL)
if not m:
    print("Could not find HTML_TEMPLATE")
    sys.exit(1)

html = m.group(1)
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)

if not scripts:
    print("No script tags found")
    sys.exit(1)

for i, script in enumerate(scripts):
    with open(f'temp_script_{i}.js', 'w', encoding='utf-8') as f:
        # Pad with empty lines so that line numbers match the HTML file
        # Find where this script started in the HTML string
        script_start = html.find(script)
        pre_html = html[:script_start]
        line_num = pre_html.count('\n')
        f.write('\n' * line_num + script)
    
    print(f"Checking script {i} starting at line {line_num}...")
    result = subprocess.run(['node', '-c', f'temp_script_{i}.js'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error in script {i}:")
        print(result.stderr)
    else:
        print(f"Script {i} is OK")
