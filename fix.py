import sys

file_path = "app.py"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False

for i, line in enumerate(lines):
    # lines are 0-indexed, so 1400 is index 1399
    if 1399 <= i <= 1523:
        if i == 1399:
            new_lines.append("          <!-- Complex calculators removed to keep UI simple -->\n")
        continue
    
    if 4489 <= i <= 4502:
        if i == 4489:
            new_lines.append('        prompt = f"""You are an expert financial advisor. The user wants an optimal mutual fund portfolio.\n')
            new_lines.append('The user is planning a {inv_type.upper()} investment of ₹{inv_amt} for a duration of {duration_years} years.\n')
            new_lines.append('Based on this profile, select exactly 2 funds from the following list (one reliable Equity index/large cap fund, and one stable Flexi cap). Assign percentage weights (must total exactly 100).\n')
            new_lines.append('Respond ONLY with a valid JSON array. Do not include any other text, markdown formatting, or explanation.\n')
            new_lines.append('Format: [{{"code": "122639", "name": "Parag Parikh Flexi Cap", "category": "Equity", "weight": 50}}, ...]\n')
            new_lines.append('\n')
            new_lines.append('Available Funds:\n')
            new_lines.append('1. Parag Parikh Flexi Cap Fund - Direct Plan - Growth (Code: 122639, Category: Equity)\n')
            new_lines.append('2. ICICI Prudential Bluechip Fund - Direct Plan - Growth (Code: 120586, Category: Equity)\n')
            new_lines.append('3. SBI Equity Hybrid Fund - Direct Plan - Growth (Code: 125497, Category: Hybrid)\n')
            new_lines.append('"""\n')
        continue
    
    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
