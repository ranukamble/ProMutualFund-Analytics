import re
import sys
import subprocess
import os

html_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

out_lines = []

# Find all script tags with their line positions in html
pattern = re.compile(r'<script(?:\s+[^>]*)?>(.*?)</script>', re.DOTALL | re.IGNORECASE)

scripts = list(pattern.finditer(html))
out_lines.append(f"Found {len(scripts)} inline script tags in {html_path}")

for idx, match in enumerate(scripts):
    script_content = match.group(1)
    # Calculate starting line number (1-based)
    start_pos = match.start(1)
    line_offset = html[:start_pos].count('\n') + 1
    out_lines.append(f"\n--- Checking Script #{idx+1} starting at line {line_offset} ({len(script_content)} chars, {script_content.count(chr(10))} lines) ---")
    
    # Save script padded with empty lines to preserve line numbers
    padded_script = ('\n' * (line_offset - 1)) + script_content
    temp_file = f"temp_script_{idx}.js"
    with open(temp_file, 'w', encoding='utf-8') as tf:
        tf.write(padded_script)
        
    try:
        res = subprocess.run(['node', '-c', temp_file], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            out_lines.append(f"Script #{idx+1}: Node syntax check PASSED OK!")
        else:
            out_lines.append(f"Script #{idx+1}: Node syntax check FAILED!")
            out_lines.append(res.stderr)
    except Exception as e:
        out_lines.append(f"Node execution failed: {e}")
        
    # Also perform a basic bracket/brace stack tracker
    stack = []
    lines = script_content.split('\n')
    in_single_quote = False
    in_double_quote = False
    in_template_lit = False
    in_line_comment = False
    in_block_comment = False
    escaped = False
    
    for l_idx, line in enumerate(lines, start=line_offset):
        col = 0
        in_line_comment = False
        while col < len(line):
            ch = line[col]
            nxt = line[col+1] if col + 1 < len(line) else ''
            
            if in_block_comment:
                if ch == '*' and nxt == '/':
                    in_block_comment = False
                    col += 1
                col += 1
                continue
            if in_line_comment:
                break
            if in_single_quote:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == "'":
                    in_single_quote = False
                col += 1
                continue
            if in_double_quote:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    in_double_quote = False
                col += 1
                continue
            if in_template_lit:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '`':
                    in_template_lit = False
                elif ch == '$' and nxt == '{':
                    stack.append(('${', l_idx, col))
                    col += 1
                col += 1
                continue
                
            # Normal code
            if ch == '/' and nxt == '/':
                in_line_comment = True
                break
            if ch == '/' and nxt == '*':
                in_block_comment = True
                col += 2
                continue
            if ch == "'":
                in_single_quote = True
                col += 1
                continue
            if ch == '"':
                in_double_quote = True
                col += 1
                continue
            if ch == '`':
                in_template_lit = True
                col += 1
                continue
            if ch in '({[':
                stack.append((ch, l_idx, col))
            elif ch in ')}]':
                expected = {'(': ')', '{': '}', '[': ']'}.get(stack[-1][0] if stack else '', '')
                if stack and (stack[-1][0] == '${' and ch == '}'):
                    stack.pop()
                elif stack and expected == ch:
                    stack.pop()
                else:
                    out_lines.append(f"Mismatched closing '{ch}' at line {l_idx}:{col}. Top of stack: {stack[-1] if stack else 'EMPTY'}")
            col += 1

    if stack:
        out_lines.append(f"Unclosed tokens at end of Script #{idx+1} (count {len(stack)}):")
        for tok in stack[-10:]:
            out_lines.append(f"  Token '{tok[0]}' opened at line {tok[1]}:{tok[2]}")

output_report = "\n".join(out_lines)
print(output_report)
with open("syntax_result.txt", "w", encoding="utf-8") as rf:
    rf.write(output_report)
