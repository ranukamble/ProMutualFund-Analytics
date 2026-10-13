import requests
import json

def guess_category(name):
    name_lower = name.lower()
    if 'liquid' in name_lower or 'cash' in name_lower or 'money market' in name_lower: return 'Liquid'
    if 'elss' in name_lower or 'tax' in name_lower: return 'Tax Saver (ELSS)'
    if 'index' in name_lower or 'etf' in name_lower or 'nifty' in name_lower or 'sensex' in name_lower: return 'Index/ETF'
    if 'debt' in name_lower or 'bond' in name_lower or 'gilt' in name_lower or 'income' in name_lower: return 'Debt'
    if 'equity' in name_lower or 'cap' in name_lower or 'bluechip' in name_lower or 'growth' in name_lower: return 'Equity'
    if 'hybrid' in name_lower or 'balanced' in name_lower or 'dynamic' in name_lower: return 'Hybrid / Balanced'
    return 'Other'

print("Downloading live active funds from AMFI...")
r = requests.get('https://www.amfiindia.com/spages/NAVAll.txt')
lines = r.text.split('\n')
schemes_list = []
for line in lines:
    parts = line.split(';')
    if len(parts) >= 6 and parts[0].strip().isdigit():
        code = parts[0].strip()
        name = parts[3].strip()
        plan = parts[4].strip()
        opt = parts[5].strip()
        
        full_name = name
        if plan and plan not in full_name:
            full_name += f" - {plan}"
        if opt and opt not in full_name:
            full_name += f" - {opt}"
            
        schemes_list.append({"code": code, "name": full_name, "category": guess_category(full_name)})

with open('active_funds.json', 'w', encoding='utf-8') as f:
    json.dump(schemes_list, f)

print(f"Success! Saved {len(schemes_list)} active, usable funds to active_funds.json")
