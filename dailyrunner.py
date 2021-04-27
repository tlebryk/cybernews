from cybernews.spiders import dailyspider as DS
import rank
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


def crawler(spiders, *args, **kwargs):
    for spider in spiders:
        settings["FEEDS"] = {
            f"{path}/{spider.source}.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
        process.crawl(spider, custom_settings=settings, *args, **kwargs)
    r = process.join()
    r.addBoth(lambda _: reactor.stop())
    return process


# cutoff is a number with number of days to go back
# for weekends, set cutoff = 3
def run_all(cutoff=1, *args, **kwargs):
    spiders = [c for _, c in inspect.getmembers(DS, inspect.isclass) if hasattr(c, "daily")]
    crawler(spiders[:4])
    reactor.run()
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


def main():
    run_all()
    df = get_todays_js()
    df = rank.sort(df)
    articles = df.to_dict("records")
    print(articles)
    return articles


if __name__ == "__main__":
    main()
