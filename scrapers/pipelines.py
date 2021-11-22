# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from app import db
from app.models import Articles
from datetime import date, datetime
import logging

TODAY = date.today()


class ScrapersPipeline:
    def open_spider(self, spider):
        self.ls = []

    def process_item(self, item, spider):
        logging.info(f"{item.get('title')}")
        self.ls.append(item)
        return item

    def close_spider(self, spider):
        return None
