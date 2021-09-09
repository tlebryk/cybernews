# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field
from itemloaders.processors import Compose, MapCompose, TakeFirst, Identity
from itemloaders import ItemLoader
from datetime import datetime
from dateutil import parser
import logging
from html_text import extract_text

def bycheck(author):
    author = author.split("By ")[-1]
    return author.strip()

def strptime(d, format1="", **kwargs):
    """ Takes date string and format and handles exceptions.
    returns "None" if cannot convert datetime"""

    if not d:
        return None
    dt = None
    try:
        dt = datetime.strptime(d, format1)
    except Exception as ex:
        logging.debug(("formated try 1 failed :", ex))
        try:
            dt = parser.parse(d, **kwargs)
        except Exception as ex:
            logging.error(("pareser try 2: %s", ex))
    finally:
        return dt

def join_body(body):
    body = [extract_text(b) for b in body if b]
    return "\n\n".join(body)

class ItemLoaderTF(ItemLoader):
    default_output_processor = TakeFirst()

class ArticleItem(scrapy.Item):

    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    author = Field(input_processor=MapCompose(bycheck), output_processor=TakeFirst())
    date = Field(input_processor=MapCompose(strptime))
    url = Field()
    source = Field()
    tags = Field()
    body = Field(input_processor=MapCompose(join_body))