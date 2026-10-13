import json, re

with open(r'C:\Users\v2spl_p5nx879\.gemini\antigravity-ide\brain\20c29e1f-d1af-4dd9-a322-e3fe2de066b5\.system_generated\steps\2884\content.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for 'expense' or 'aum' using regex
aum_matches = re.findall(r'.{0,50}aum.{0,50}', content, re.IGNORECASE)
print("AUM Matches:", len(aum_matches))
for i, m in enumerate(aum_matches[:10]):
    print(f"[{i}]: {m}")

expense_matches = re.findall(r'.{0,50}expense_ratio.{0,50}', content, re.IGNORECASE)
print("\nExpense Matches:", len(expense_matches))
for i, m in enumerate(expense_matches[:10]):
    print(f"[{i}]: {m}")
