from spiders import dailyspider as DS
import pandas as pd
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json
import os
import importlib, inspect
import time
# for name, cls in inspect.getmembers(importlib.import_module("myfile"), inspect.isclass):
#     print(name)
#     print(cls)

today = date.today().strftime("%B_%d_%Y")
path = f"jsons/{today}"
if not os.path.isdir(path):
    os.mkdir(path)

def crawler(spiders, *args, **kwargs):
    settings = get_project_settings()
    settings["ITEM_PIPELINES"] = {
        'cybernews.pipelines.CyberNewsPipeline': 300
    }
    process = CrawlerProcess(settings)
    for spider in spiders:
        settings["FEEDS"] = {
            f"{path}/{spider.source}.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
        process.crawl(spider, custom_settings=settings)
    return process

if __name__ == "__main__":
    # spider = DS.LawfareDaily
    # process = crawler([spider])
    # process.start()
    start = time.process_time()
    spiders = [cl for _name, cl in inspect.getmembers(DS, inspect.isclass) if hasattr(cl,"daily")]
    process = crawler(spiders)
    process.start()

final_dcts = []
for f in os.listdir(path):
    if f.endswith(".json"):
        fname = f"{path}/{f}"
        with open(fname, "r", encoding='utf-8') as fil:
            x = fil.read()
            if x:
                fil.seek(0)
                final_dcts.append(json.load(fil))
finalpath = f"{path}/final"
if not os.path.isdir(finalpath):
    os.mkdir(finalpath)
with open(f"{finalpath}/{today}.json", 'w', encoding='utf8') as fout:
    json.dump(final_dcts, fout, ensure_ascii=False)
print(f"Total time {time.process_time() - start}")


# using crawler runner deffered crawls (much slower)
# runner = CrawlerRunner
# @defer.inlineCallbacks
# def crawler(spiders, *args, **kwargs):
#     for spider in spiders:
#         yield runner.crawl(spider)

# if __name__ == "__main__":

#     print("[")

#     spiders = [cl for _name, cl in inspect.getmembers(DS, inspect.isclass) if hasattr(cl,"daily")]
#     crawler(spiders)
#     reactor.run()
#     print("{}\n]")

