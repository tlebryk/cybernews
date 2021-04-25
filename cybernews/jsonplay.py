import json
import os
from datetime import date, datetime, timedelta

today = date.today().strftime("%B_%d_%Y")
path = f"jsons/{today}/"
final_dcts = []
for f in os.listdir(path):
    print(f)
    if f.endswith(".json"):
        fname = f"{path}{f}"
        with open(fname, "r", encoding='utf-8') as fil:
            x = fil.read()
            if x:
                fil.seek(0)
                final_dcts.append(json.load(fil))
    with open(f"{path}final/{today}.json", 'w', encoding='utf8') as fout:
        json.dump(final_dcts, fout, ensure_ascii=False)