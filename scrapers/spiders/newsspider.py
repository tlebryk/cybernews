"""Generic Spider to get news article metadata"""
import logging
import scrapy
from datetime import date, datetime, timedelta
from html_text import extract_text
from urllib.parse import urljoin
from dateutil import parser
import re
import json


class NewsSpider(scrapy.Spider):
    recent_urls = []
    name = "newspider"
    source = name
    today = datetime.today()
    # NOTE: will eventually come from last time script ran
    # for now, round down to midnight
    current_time = timedelta(hours=today.hour, minutes=today.minute + 1)
    cutoff = today - timedelta(1) - current_time
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0"
    }
    # Not fully implemented: need to test as a check during start_requests? 
    # open question: what if urls aren't chronological? 
    # should have a "is_chronological" arg that defaults to true for each daily. 
    stopcollection = False

    # make sure start_urls and date_check are defined even if None
    def __init__(self, *args, **kwargs):
        if kwargs.get("start_urls"):
            self.start_urls = kwargs.pop("start_urls")
        if not hasattr(self, "date_check"):
            self.date_check = kwargs.pop("date_check")
        if type(self.date_check) == str:
            self.logger.info(f"found string in datecheck {self.date_check}")
            if self.date_check.lower() == "false":
                self.logger.info(f"Changing date_check to false:")
                kwargs["date_check"] = False
                # default for a string is True so any string other than false will return true
        if kwargs.get("cutoff"):
            self.logger.info(f"kwarg cutoff: {kwargs.get('cutoff')}")
            if self.strptime(kwargs.get("cutoff")):
                self.logger.info(f"kwarg strptime: {self.strptime(kwargs.get('cutoff'))}")
                self.cutoff = self.strptime(kwargs.pop("cutoff"))
        if kwargs.get("articles"):
            self.articles = kwargs.get("articles")
        else:
            self.articles = []
        self.__dict__.update(kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        self.logger.info(f"Starting collection on {response.url}")
        return self.art_parse(response, dt=None, date_check=self.date_check)

    # removes by from bylines
    def bycheck(self, author):
        author = author.split("By ")[-1]
        return author.strip()

    def strptime(self, d, format1="", **kwargs):
        """ Takes date string and format and handles exceptions.
        returns "None" if cannot convert datetime"""

        if not d:
            return None
        dt = None
        try:
            dt = datetime.strptime(d, format1)
        except Exception as ex:
            self.logger.debug(("formated try 1 failed :", ex))
            try:
                dt = parser.parse(d, **kwargs)
            except Exception as ex:
                self.logger.error(("pareser try 2: %s", ex))
        finally:
            return dt

    def cutoff_check(self, url, dt=None):
        """ takes datetime, returns True if after last
        
        If date is before miniumum date, returns false and turns stop collection 
        to True"""
        if not dt:
            self.logger.warning("Can't confirm %s date", url)
            return True
        if dt < self.cutoff:
            self.logger.info(f"{dt} is less than cutoff {self.cutoff}; ending collection")
            self.stopcollection = True
            return False
        else:
            return True

    # returns true URL already covered in recent briefing
    # important for articles without time to check
    # TODO: Current behavior is to continue;
    # alternative is to break once previous article found
    def in_urls(self, url):
        return url in self.recent_urls

    def get_tags(self, response):
        return None

    def get_title(self, response, splitchar=None, splitchar2=None):
        title = extract_text(response.css("title").get())
        if splitchar:
            title = title.split(splitchar)[:-1]
            title = " ".join(title)
        if not title:
            title = extract_text(response.css(".title").get())
            if splitchar2:
                title = title.split(splitchar2)[:-1]
                title = " ".join(title)
        return title

    def get_body(self, response):
        body = extract_text(response.css("div.article-inner-content").get())
        if body:
            return body
        else:
            return extract_text(response.css(".body").get())

    # takes xpath selector return, extracts text, and joins.
    def join_body(self, body):
        body = [extract_text(b.get()) for b in body if b.get()]
        return "\n\n".join(body)

    # Get_dt should return a datetime object,
    # which we convert in the article parse section at the end
    # into a string of format into "Month day, year" format
    def get_dt(self, response, **kwargs):
        dt = extract_text(response.css("time").get())
        dt = self.strptime(dt, format1="", **kwargs)
        return dt

    def get_author(self, response):
        author = response.xpath("//meta[contains(@*, 'author')]/@content").get()
        if not author:
            author = extract_text(response.css(".author").get())
        return self.bycheck(author)

    def art_parse(self, response, dt=None, date_check=True):
        if not dt:
            dt = self.get_dt(response)
        if dt and date_check:
            if dt < self.cutoff:
                self.logger.info(f"Date was before minimum date for url {response.url}")
                return None
        # attempt to convert into Month, day, year format
        if isinstance(dt, date) or isinstance(dt, datetime):
            dt = dt.strftime("%B %d, %Y")
        art_dict = {
            "title": self.get_title(response),
            "author": self.get_author(response),
            "date": dt,
            "url": response.url,
            "source": self.source,
            "tags": self.get_tags(response),
            "body": self.get_body(response),
        }
        self.articles.append(art_dict)
        self.logger.info(f"Ending collection on {response.url} and returning dict from artparse")
        return art_dict
