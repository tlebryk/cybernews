import os
import zipfile
import xml.etree.ElementTree as ET
from docx import Document
import re
from datetime import datetime
import json
import csv
import logging
import traceback
from spiders import articlesspider as AS
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter


Febpath = "C:/Users/tlebr/OneDrive - DEFDEM/Theo Lebryk/Daily Clippings/February/"
Marpath = "C:/Users/tlebr/OneDrive - DEFDEM/Theo Lebryk/Daily Clippings/March/"


logging.basicConfig(
    filename="oldarts.log", encoding="utf-8", filemode="w", level=logging.DEBUG
)
# returns list of tuples (url, ranking, filename)
def get_links(path):
    links = []
    for filename in os.listdir(path):
        f = path + filename
        with zipfile.ZipFile(f) as z:
            d = z.read("word/document.xml")
        xml_str = str(d)
        # [1:] gets rid of microsoft random urls
        link_list = re.findall(r"http.*?\<", xml_str)[1:]
        # strips trailing ">" from urls
        link_list = [(x[:-1], i + 1, filename) for i, x in enumerate(link_list)]
        links += link_list
    return links


if __name__ == "__main__":
    settings = get_project_settings()
    settings["FEEDS"] = {
        "test1.json": {"format": "json", "encoding": "utf8", "overwrite": False}
    }
    settings["LOG_LEVEL"] = "INFO"
    links = get_links(path=Febpath) + get_links(path=Marpath)
    process = AS.get_articles(links, settings)
    process.start()
    datapath = "C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\data\\"
    with open(datapath + "oldarts.json", "w", encoding="utf-8") as fp:
        s = json.dumps(AS.DICT_LS, ensure_ascii=False, indent="\t")
        fp.write(s)
    with open(datapath + "oldarts.csv", "w", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=AS.DICT_LS[0].keys())
        writer.writeheader()
        for data in AS.DICT_LS:
            writer.writerow(data)
