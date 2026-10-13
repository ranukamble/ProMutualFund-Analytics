import os

def refactor():
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    start_marker = 'HTML_TEMPLATE = """\n'
    end_marker = '"""\n'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("HTML_TEMPLATE not found.")
        return
        
    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        print("End of HTML_TEMPLATE not found.")
        return
        
    html_content = content[start_idx + len(start_marker):end_idx]
    
    os.makedirs("templates", exist_ok=True)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Replace the HTML_TEMPLATE string with nothing, and add import render_template if not exists
    new_content = content[:start_idx] + content[end_idx + len(end_marker):]
    
    if "from flask import" in new_content and "render_template" not in new_content:
        new_content = new_content.replace("from flask import Flask,", "from flask import Flask, render_template,")
        
    # Replace return render_template_string(HTML_TEMPLATE) with return render_template("index.html")
    new_content = new_content.replace("return render_template_string(HTML_TEMPLATE", 'return render_template("index.html"')
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print("Successfully refactored! Extracted index.html to templates/ and updated app.py")

if __name__ == "__main__":
    refactor()
