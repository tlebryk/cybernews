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
    cutoff = today - timedelta(1)
    custom_settings = {"FEED_EXPORT_ENCODING": "utf-8"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0"
    }

    # make sure start_urls and date_check are defined even if None
    def __init__(self, *args, **kwargs):
        self.start_urls = kwargs.get('start_urls')
        self.date_check = kwargs.get('date_check')
        self.articles = kwargs.get('articles')
        self.__dict__.update(kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        pass

    # removes by from bylines
    def bycheck(self, author):
        author = author.split("By")[-1]
        return author.strip()

    # takes date string and format and handles exceptions,
    # returns "None" if cannot convert datetime
    def strptime(self, d, format1):
        if not d:
            return None
        dt = None
        try:
            dt = datetime.strptime(d, format1)
        except Exception as ex:
            self.logger.error(("formated try 1 failed :", ex))
            try:
                dt = parser.parse(d)
            except Exception as ex:
                self.logger.error(("pareser try 2: %s", ex))
        finally:
            return dt

    # takes datetime, returns True if after last
    # default returns true for sites where date cannot  be determined
    def cutoff_check(self, url, dt=None):
        if not dt:
            self.logger.warning("Can't confirm %s date", url)
            return True
        return dt >= self.cutoff

    # returns true URL already covered in recent briefing
    # important for articles without time to check
    # TODO: Current behavior is to continue;
    # alternative is to break once previous article found
    def in_urls(self, url):
        print(f"URL in urls: {url in self.recent_urls}\n\n")
        return url in self.recent_urls

    def get_tags(self, response):
        return None

    def get_title(self, response, splitchar=None, splitchar2=None):
        title = extract_text(response.css("title").get())
        if splitchar:
            title = title.split(splitchar)[0]
        if not title:
            title = extract_text(response.css(".title").get())
            if splitchar2:
                title = title.split(splitchar2)[0]
        return title

    def get_body(self, response):
        return extract_text(response.css(".body").get())

    # takes xpath selector return, extracts text, and joins.
    def join_body(self, body):
        body = [extract_text(b.get()) for b in body if b.get()]
        return "\n\n".join(body)

    def get_dt(self, response):
        return extract_text(response.css("time").get())

    def get_author(self, response):
        author = response.xpath("//meta[contains(@*, 'author')]/@content").get()
        if not author:
            author = extract_text(response.css(".author").get())
        return self.bycheck(author)

    # TODO: need get_dt to only pass datetime object [check that not passing date]
    # handle dates not getting found.
    # If date_check, don't take old articles.
    def art_parse(self, response, dt=None, date_check=True):
        if not dt:
            dt = self.get_dt(response)
        if dt and date_check:
            if dt < self.cutoff:
                return None
        art_dict = {
            "title": self.get_title(response),
            "author": self.get_author(response),
            "date": dt.strftime("%B %d, %Y"),
            "url": response.url,
            "source": self.source,
            "tags": self.get_tags(response),
            "body": self.get_body(response),
        }
        self.articles.append(art_dict)
        print(self.logger.WARNING(f"{self.articles}"))
        return art_dict
