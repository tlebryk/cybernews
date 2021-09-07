import pickle 
import pandas as pd
import json
from datetime import date, datetime, timedelta
import os

HOMEDIR = os.path.expanduser("~")


analyze = pickle.load(open("cybernews/models/analyze2.pickle", "rb"))
gbm = pickle.load(open("cybernews/models/gbm2.pickle", "rb"))

# takes df, generates rankings, and returns sorted df based on rankings
def sort(df):
    trans = analyze.transform(df["body"]).astype('float32')
    preds = gbm.predict(trans)
    print(preds)
    df['preds'] = preds
    df.fillna(value="None", inplace=True)
    # df = df.drop("Tags", axis=1)
    return df.sort_values("preds")
