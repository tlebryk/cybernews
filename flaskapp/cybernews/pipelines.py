# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from datetime import date

today = date.today().strftime(r"%B_%d_%Y")

class CyberNewsPipeline:
    article_counter = 0

    def open_spider(self, spider):
        self.file = open(today + spider.source + ".json", "w")  
        pass


    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        self.article_counter+=1
        return item

    def close_spider(self, spider):
        self.file.close()

class JsonWritePipeline:
    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        return item