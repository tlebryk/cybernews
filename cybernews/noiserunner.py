from spiders import noise
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import date, datetime, timedelta
import json


oldpath = (
    "C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\data\\oldarts.json"
)
with open(oldpath, encoding="utf-8") as f:
    s = json.load(f)
df = pd.json_normalize(s)
urls = list(df.url)

# feeds is a dict with output file location
def crawler(Spider, *args, **kwargs):
    settings = get_project_settings()
    settings["FEEDS"] = {
        f"{Spider.name}.json": {
            "format": "json",
            "encoding": "utf8",
            "overwrite": True,
        }
    }
    # settings[
    #     "LOG_FILE"
    # ] = "C:/Users/tlebr/Google Drive/fdd/dailynews/cybernews/cybernews/logs/noise.log"
    process = CrawlerProcess(settings)
    process.crawl(Spider, **kwargs)
    print(settings)
    return process




if __name__ == "__main__":

    earliest = datetime(2021, 2, 11)
    latest = datetime.today()
    process = crawler(
        noise.CyberScoopNoise, **dict(earliest=earliest, latest=latest, recent_urls=urls)
    )
    process.start()