import json
import time
import pandas as pd
from app import get_quote, get_advanced
import os

print("Starting the massive 40,000 fund data downloader...")
print("This will take many hours because we have to pause between requests so Groww doesn't ban us.")

# Load all 40,000 codes
with open('scheme_codes.json', 'r') as f:
    all_funds = json.load(f)

codes = list(all_funds.keys())
total = len(codes)

output_file = 'all_funds_powerbi.csv'

# Load existing progress if script was stopped and restarted
if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file)
    completed_codes = set(existing_df['code'].astype(str))
    print(f"Resuming... Already finished {len(completed_codes)} funds.")
else:
    completed_codes = set()
    # Create empty CSV with headers
    pd.DataFrame(columns=[
        'code', 'name', 'nav', 'nav_date', 'aum', 'expense_ratio', 
        'fund_manager', 'exit_load', 'risk', 'return_1yr', 'return_3yr', 'return_5yr', 'high_52', 'low_52'
    ]).to_csv(output_file, index=False)

for i, code in enumerate(codes):
    if code in completed_codes:
        continue
        
    try:
        print(f"[{i}/{total}] Fetching {code} - {all_funds[code]}...")
        
        # We must push a Flask app context to use the functions from app.py locally
        from app import app
        with app.test_request_context(f'/api/quote/{code}?api_key=POWER_BI_KEY_2026'):
            q_out = get_quote(code)
            q_res = q_out[0].get_json() if isinstance(q_out, tuple) else q_out.get_json()
            
        with app.test_request_context(f'/api/advanced/{code}?api_key=POWER_BI_KEY_2026'):
            a_out = get_advanced(code)
            a_res = a_out[0].get_json() if isinstance(a_out, tuple) else a_out.get_json()
            
        if "error" not in q_res:
            quote = q_res.get("quote", {})
            scraped = q_res.get("scraped", {})
            
            # Format managers if array
            fm = scraped.get('fund_manager', 'N/A')
            if isinstance(fm, list):
                fm = ", ".join([str(m) for m in fm])
                
            row = {
                'code': code,
                'name': all_funds[code],
                'nav': quote.get('nav'),
                'nav_date': quote.get('date'),
                'aum': scraped.get('aum'),
                'expense_ratio': scraped.get('expense_ratio'),
                'fund_manager': fm,
                'exit_load': scraped.get('exit_load'),
                'risk': scraped.get('risk'),
                'return_1yr': a_res.get('return_1yr'),
                'return_3yr': a_res.get('return_3yr'),
                'return_5yr': a_res.get('return_5yr'),
                'high_52': a_res.get('high_52'),
                'low_52': a_res.get('low_52')
            }
            
            # Append this single row to the CSV immediately so we don't lose data if it crashes
            pd.DataFrame([row]).to_csv(output_file, mode='a', header=False, index=False)
            
        # VERY IMPORTANT: Sleep for 1.5 seconds so external servers don't ban our IP address
        time.sleep(1.5)
        
    except Exception as e:
        print(f"Skipping {code} due to error: {e}")
        time.sleep(1.5)

print("\nDONE! All funds have been downloaded to all_funds_powerbi.csv")
