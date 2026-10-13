import requests
r = requests.get('https://groww.in/v1/api/data/mf/web/v1/scheme/search/parag-parikh-long-term-equity-fund-direct-growth', headers={'User-Agent': 'Mozilla/5.0'})
if r.ok:
    data = r.json()
    print("Keys:", list(data.keys()))
    print("Expense Ratio:", data.get('expense_ratio'))
    print("Asset Allocation:", data.get('asset_allocation', 'None'))
    print("Market Cap:", data.get('market_cap', 'None'))
else:
    print(r.status_code)
