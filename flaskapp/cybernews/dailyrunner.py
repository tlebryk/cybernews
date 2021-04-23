from spiders import dailyspider as DS
import pandas as pd
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
from twisted.internet import reactor, defer
import json
import importlib, inspect


settings = get_project_settings()
settings["FEEDS"] = {
    "test12.json": {
        "format": "json",
        "encoding": "utf8",
        "overwrite": False,
    }
}
runner = CrawlerRunner(settings)

settings["ITEM_PIPELINES"] = {
    'cybernews.pipelines.CyberNewsPipeline': 300
}

# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(Spider1)
#     yield runner.crawl(Spider2)
#     reactor.stop()

@defer.inlineCallbacks
def crawler(spiders, *args, **kwargs):
    for spider in spiders:
        yield runner.crawl(spider)
    reactor.stop()


if __name__ == "__main__":
    # spider = DS.LawfareDaily
    # process = crawler([spider])
    # process.start()
    print("[")
    today = date.today().strftime(r"%B_%d_%Y")
    path = today + '.json'
    # f with open(today + ".json", "w") 
    #     f.write("[")
    spiders = [cl for _name, cl in inspect.getmembers(DS, inspect.isclass) if hasattr(cl,"daily")]
    crawler(spiders)
    reactor.run()
    print("{}\n]")

        # f.write("f")
