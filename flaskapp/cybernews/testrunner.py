from spiders.test import InsideCSArt
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess


if __name__ == "__main__":
    settings = get_project_settings()
    settings["FEEDS"] = {
        "test1.json": {"format": "json", "encoding": "utf8", "overwrite": True}
    }
    settings["ITEM_PIPELINES"] = {"cybernews.pipelines.JsonWritePipeline": 300}
    # settings["LOG_LEVEL"] = "INFO"
    process = CrawlerProcess(settings)
    d = {
        "start_urls": [
            "https://insidecybersecurity.com/daily-news/cisa-leaders-house-appropriators-expanded-visibility-federal-networks-requires-more"
        ],
        "start_urls2": [
            "https://insidecybersecurity.com/daily-news/lawmakers-federal-officials-begin-examining-next-set-cyber-policy-needs-amid-covid-and",
            "https://insidecybersecurity.com/daily-news/policy-leader-highlights-cyber-insurance-role-policymakers-begin-shifting-focus",
        ],
    }
    process.crawl(InsideCSArt, **d)
    process.start()
