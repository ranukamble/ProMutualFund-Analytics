import requests
from datetime import datetime

portfolio_items = [
    {"code": "122639", "allocation_pct": 0.25},
    {"code": "112628", "allocation_pct": 0.25},
    {"code": "148665", "allocation_pct": 0.25},
    {"code": "120586", "allocation_pct": 0.25}
]

fund_data = []
for item in portfolio_items:
    resp = requests.get(f"https://api.mfapi.in/mf/{item['code']}")
    mf_data = resp.json()
    nav_list = mf_data['data']
    nav_dict = {}
    for entry in nav_list:
        d = datetime.strptime(entry['date'], '%d-%m-%Y')
        nav_dict[d] = float(entry['nav'])
    fund_data.append({'nav_dict': nav_dict})
    print(f"{item['code']} has {len(nav_dict)} points")

all_date_sets = [set(f['nav_dict'].keys()) for f in fund_data]
common_dates = set.intersection(*all_date_sets)
print(f"Common dates: {len(common_dates)}")
