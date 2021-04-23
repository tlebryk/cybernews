from spiders import dailyspider as DS
import pandas as pd
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json
import importlib, inspect
# for name, cls in inspect.getmembers(importlib.import_module("myfile"), inspect.isclass):
#     print(name)
#     print(cls)

today = date.today().strftime("%B_%d_%Y")

def crawler(spiders, *args, **kwargs):
    settings = get_project_settings()
    settings["ITEM_PIPELINES"] = {
        'cybernews.pipelines.CyberNewsPipeline': 300
    }
    process = CrawlerProcess(settings)
    for spider in spiders:
        settings["FEEDS"] = {
            f"jsons/{today}_{spider.source}.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": False,
            }
        }
        process.crawl(spider, custom_settings=settings)
    return process

if __name__ == "__main__":
    # spider = DS.LawfareDaily
    # process = crawler([spider])
    # process.start()

    spiders = [cl for _name, cl in inspect.getmembers(DS, inspect.isclass) if hasattr(cl,"daily")]
    process = crawler(spiders)
    process.start()

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

