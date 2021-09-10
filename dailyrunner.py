
"""Script to scrap news articles every day.

TODO: refactor to stop using globals. 
Currently formatted this way because twistied does not play well with flask wgsi. 
Need to define a reactor and process within a separate script instead of in the main app
because twisted-wgsi conflicts. 
TODO: logging
"""
from cybernews.spiders import dailyspider as DS
# import rank
import pandas as pd
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json
import os
import importlib, inspect
from twisted.internet import reactor

TODAY = datetime.today().strftime("%B_%d_%Y")
# current_time = timedelta(hours=t.hour, minutes=t.minute + 1)
PATH = f"jsons/{TODAY}"
if not os.path.isdir(PATH):
    os.makedirs(PATH)
settings = get_project_settings()
PROCESS = CrawlerRunner(settings)


def crawler(spiders, process, *args, **kwargs):
    """Returns blueprints for a crawl but does not actually send requests
    
    :spiders: list of spiders to crawl from
    :process: generic crawler with certain settings
    returns: ___ objects which can be run with reactor.run()
    """
    for spider in spiders:
        settings["FEEDS"] = {
            f"{PATH}/{spider.source}.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
        process.crawl(spider, custom_settings=settings, *args, **kwargs)
    return process


# cutoff is a number with number of days to go back
# for weekends, set cutoff = 3
def run_all(cutoff=1, process=PROCESS, *args, **kwargs):
    """Collects all spiders from dailyspider and passes them to crawler"""
    spiders = [c for _, c in inspect.getmembers(DS, inspect.isclass) if hasattr(c, "daily")]
    return crawler(spiders, process)

def write_final_dict():
    """Reads individual jsons created by each spider and combines into 1 json

    Reads from jsons/monday_day_year/spider_name.json
    writes to jsons/month_day_year/final/month_day_year.json
    """
    final_dcts = []
    # read all json files the spider wrote to
    for f in os.listdir(PATH):
        if f.endswith(".json"):
            fname = f"{PATH}/{f}"
            with open(fname, "r", encoding="utf-8") as fil:
                x = fil.read()
                if x:
                    fil.seek(0)
                    final_dcts += json.load(fil)
    finalpath = f"{PATH}/final"
    if not os.path.isdir(finalpath):
        os.mkdir(finalpath)
    with open(f"{finalpath}/{TODAY}.json", "w", encoding="utf8") as fout:
        json.dump(final_dcts, fout, ensure_ascii=False)


# converts final json into dataframe
def get_todays_js():
    """Convert today's final json into a dataframe
    
    Essentially datawrangling for ranking algo"""
    p = f"{PATH}/final/{TODAY}.json"
    df = pd.read_json(p)
    return df


# def main(process=PROCESS, n=7):
#     """Sets off scrapers, writes results to json, and ranks articles, only returning top n
# 
#       Not yet functional: rank needs to be fixed"""
#     run_all(process=process)
#     df = get_todays_js()
#     df = rank.sort(df)
#     df = df.loc[:n]
#     articles = df.to_json(orient="records")
#     a = json.loads(articles)
#     return a


def full(process=PROCESS):
    """Sets off scrapers and writes results to final json"""
    r = run_all(process=process)
    r = process.join()
    # run sequentially and block until the process finishes
    r.addBoth(lambda _: reactor.stop())
    reactor.run()
    write_final_dict()
    df = get_todays_js()
    # df = rank.sort(df)
    articles = df.to_json(orient="records")
    a = json.loads(articles)
    # print(a)

if __name__ == "__main__":
    full(PROCESS)
