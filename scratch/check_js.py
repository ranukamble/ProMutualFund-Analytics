import re
import subprocess

with open('c:/Users/v2spl_p5nx879/Downloads/mftool-master/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the script block
match = re.search(r'(const pg = \(\(\) => \{.*?\})\(\);)', content, re.DOTALL)
if match:
    js = match.group(1)
    with open('c:/Users/v2spl_p5nx879/Downloads/mftool-master/scratch/test_js.js', 'w', encoding='utf-8') as out:
        out.write(js)
    print("Extracted JS.")
else:
    print("Could not find JS block")
