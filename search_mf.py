from mftool import Mftool
import requests
from datetime import datetime

mf = Mftool()
all_codes = mf.get_scheme_codes()

funds_to_find = ["HDFC Mid", "SBI Equity Hybrid", "ICICI Prudential Bluechip", "Axis Midcap", "Mirae Asset Large", "Quant Small Cap", "UTI Nifty 50 Index"]

for f in funds_to_find:
    matches = {k: v for k, v in all_codes.items() if f.lower() in v.lower() and "direct" in v.lower() and "growth" in v.lower()}
    if matches:
        print(f"\n{f}:")
        for k, v in matches.items():
            print(f"{k} : {v}")
