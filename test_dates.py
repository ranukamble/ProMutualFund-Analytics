import requests
from datetime import datetime

codes_to_check = [
    ("Parag Parikh Flexi Cap", "122639"),
    ("ICICI Prudential Bluechip", "120586"),
    ("Nippon India Small Cap", "118778"),
    ("SBI Equity Hybrid", "125497"), # guessing
    ("Axis Midcap", "120505"),
    ("Mirae Asset Large Cap", "107578")
]

for name, code in codes_to_check:
    try:
        r = requests.get(f'https://api.mfapi.in/mf/{code}').json()
        dates = [datetime.strptime(e['date'], '%d-%m-%Y') for e in r['data']]
        dates.sort()
        print(f"{name} ({code}): {dates[0].date()} to {dates[-1].date()}")
    except Exception as e:
        print(f"Error {code}: {e}")
