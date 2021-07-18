
"""Script to scrap news articles every day"""
from cybernews.spiders import dailyspider as DS
# import rank
import pandas as pd
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json
import os
import importlib, inspect
import time
from twisted.internet import reactor

t = datetime.today()
today = t.strftime("%B_%d_%Y")
current_time = timedelta(hours=t.hour, minutes=t.minute + 1)
path = f"jsons/{today}"
if not os.path.isdir(path):
    os.mkdir(path)
settings = get_project_settings()
process = CrawlerRunner(settings)


def crawler(spiders, process, *args, **kwargs):
    for spider in spiders:
        settings["FEEDS"] = {
            f"{path}/{spider.source}.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
        process.crawl(spider, custom_settings=settings, *args, **kwargs)
    return process


# cutoff is a number with number of days to go back
# for weekends, set cutoff = 3
def run_all(cutoff=1, process=process, *args, **kwargs):
    spiders = [c for _, c in inspect.getmembers(DS, inspect.isclass) if hasattr(c, "daily")]
    return crawler(spiders, process)

def write_final_dict():
    final_dcts = []
    for f in os.listdir(path):
        if f.endswith(".json"):
            fname = f"{path}/{f}"
            with open(fname, "r", encoding="utf-8") as fil:
                x = fil.read()
                if x:
                    fil.seek(0)
                    final_dcts += json.load(fil)
    finalpath = f"{path}/final"
    if not os.path.isdir(finalpath):
        os.mkdir(finalpath)
    with open(f"{finalpath}/{today}.json", "w", encoding="utf8") as fout:
        json.dump(final_dcts, fout, ensure_ascii=False)


# converts final json into dataframe
def get_todays_js():
    p = f"{path}/final/{today}.json"
    df = pd.read_json(p)
    return df


def main(process=process):
    run_all(process=process)
    df = get_todays_js()
    # df = rank.sort(df)
    # df = df.loc[:7]
    articles = df.to_json(orient="records")
    a = json.loads(articles)
    return a


def full(process=process):
    r = run_all(process=process)
    r = process.join()
    r.addBoth(lambda _: reactor.stop())
    reactor.run()
    write_final_dict()
    df = get_todays_js()
    # df = rank.sort(df)
    articles = df.to_json(orient="records")
    a = json.loads(articles)
    print(a)

if __name__ == "__main__":
    full(process)
