import requests

codes = ["122639", "112628", "148665", "145552", "120586", "120505", "107578", "120828", "120716"]
for c in codes:
    try:
        r = requests.get(f'https://api.mfapi.in/mf/{c}').json()
        print(f"Code {c}: {len(r.get('data', []))} nav points")
    except Exception as e:
        print(f"Code {c}: ERROR {e}")
