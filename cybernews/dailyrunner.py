from spiders import dailyspider
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json
import importlib, inspect
# for name, cls in inspect.getmembers(importlib.import_module("myfile"), inspect.isclass):
#     print(name)
#     print(cls)

def crawler(spiders, *args, **kwargs):
    settings = get_project_settings()
    settings["FEEDS"] = {
        "test.json": {
            "format": "json",
            "encoding": "utf8",
            "overwrite": False,
        }
    }
    process = CrawlerProcess(settings)
    for spider in spiders:
        process.crawl(spider)
    return process

if __name__ == "__main__":
    spiders = [cl for _name, cl in inspect.getmembers(dailyspider, inspect.isclass) if hasattr(cl,"parse")]
    process = crawler(spiders)
    process.start()