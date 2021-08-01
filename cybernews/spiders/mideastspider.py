import scrapy
from datetime import date, datetime, timedelta
from html_text import extract_text
import html2text
from urllib.parse import urljoin
from dateutil import parser
import pandas as pd
import re
import json
from .newsspider import NewsSpider

# # Password file not included  in repo. 
# import sys
# sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
# import pws


converter = html2text.HTML2Text()
converter.ignore_links = True


class Kurd24Art(NewsSpider):
    name = "Kurd24Art"
    source = "Kurdistan 24"

    # def __init__(self, *args, **kwargs):
    #     path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
    #     df2 = pd.read_excel(path2)
    #     kurd24 = df2[df2.Source.str.lower().str.strip() == "kurdistan 24"]
    #     kurd24 = kurd24[kurd24.Url.notna()]
    #     self.start_urls = [str(url) for url in list(kurd24.Url)]
    #     self.date_check = False
    #     self.articles = []
        # super().__init__(*args, **kwargs)

    def parse(self, response):
        return self.art_parse(response, dt=None, date_check=self.date_check) 

    def get_author(self, response):
        return self.bycheck(extract_text(response.css("span.Name-Author").get()))

    def get_body(self, response):
        return extract_text(response.css("div.News-reader-video-title").get())
    
    def get_dt(self, response):
        # try:
        #     dt = super().get_dt(response)
        # except:
        dt = extract_text(response.css("time").get())
        dt = self.strptime(dt, "%Y/%m/%d %H:%M")
        return dt 

    def get_tags(self, response):
        tags = response.css("a.video-links")
        tags = [extract_text(tag.get()).strip() for tag in tags]
        return tags
        return super().get_tags(response)


class ReutersArt(NewsSpider):
    # todo: get paywall arguments

    name = "ReutersArt"
    source = "Reuters"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_title(self, response, splitchar="|", splitchar2=None):
        return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)
    
    def get_dt(self, response):
        dt = response.xpath("//meta[contains(@name, 'REVISION_DATE')]/@content").get()
        dt = self.strptime(dt, "")
        return dt

    def get_body(self, response):
        body =  response.css("p.Paragraph-paragraph-2Bgue")
        return self.join_body(body)

    def __init__(self, *args, **kwargs):
        path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
        df2 = pd.read_excel(path2)
        reuters = df2[df2.Source.str.lower().str.strip() == "reuters"]
        reuters = reuters[reuters.Url.notna()]
        kwargs["start_urls"] = [str(url) for url in list(reuters.Url)]
        self.articles = []
        super().__init__(*args, **kwargs)
        # self.date_check = False
    
    def parse(self, response):
        return self.art_parse(response, dt=None, date_check=self.date_check)



class AlmontArt(NewsSpider):
    name = "AlmontArt"
    source = "Al-monitor"

    def __init__(self, *args, **kwargs):
        path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
        df2 = pd.read_excel(path2)
        stories = df2[df2.Source.str.lower().str.strip() == "al-monitor"]
        stories = stories[stories.Url.notna()]
        kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
        self.articles = []
        super().__init__(*args, **kwargs)


    def get_title(self, response, splitchar="-", splitchar2=None):
        return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)
    
    def get_author(self, response):
        return extract_text(response.css("div.author-title").get())
    
    def get_body(self, response):
        return extract_text(response.css("div.field--name-body").get())
    
    def get_tags(self, response):
        tags = response.css("div.topic").getall()
        tags = [extract_text(tag) for tag in tags]
        return tags
    

class SPGlobalArt(NewsSpider):
    name = "SPGlobalArt"
    source = 'S&P Global Platts'

    def __init__(self, *args, **kwargs):
        path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
        df2 = pd.read_excel(path2)
        stories = df2[df2.Source.str.lower().str.strip() == "s&p global platts"]
        stories = stories[stories.Url.notna()]
        kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
        super().__init__(*args, **kwargs)

    def get_tags(self, response):
        tags = response.xpath("//meta[contains(@property, 'commodity')]/@content").get()
        tags = tags.split("|")
        return tags

    def get_author(self, response):
        return response.xpath("//a[contains(@data-gtm-action, 'Author')]/text()").get()

    def get_title(self, response, splitchar="|", splitchar2=None):
        return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

    def get_dt(self, response):
        dt = extract_text(response.css("li.meta-data__date").get())
        # remove trailing timezone
        dt = " ".join(dt.split(" ")[:-1])
        dt = self.strptime(dt, "%d %b %Y | %H:%M")
        return dt

    def get_body(self, response):
        body = response.css("div.article__content")
        body = self.join_body(body)
        return body

    
class APArt(NewsSpider):
    name = "APArt"
    source = 'AP News'

    def __init__(self, *args, **kwargs):
        path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx",
        df2 = pd.read_excel(path2)
        stories = df2[df2.Source.str.lower().str.strip() == "ap news"]
        stories = stories[stories.Url.notna()]
        kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
        super().__init__(*args, **kwargs)

    def get_tags(self, response):
        tags = response.css("li.tag")
        tags = [extract_text(tag.get()) for tag in tags]

    def get_author(self, response):
        author = extract_text(response.css("span.Component-bylines-0-2-63").get())
        return self.bycheck(author)

    def get_title(self, response, splitchar, splitchar2):
        return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

    def get_body(self, response):
        return extract_text(response.css("div.Article").get())

    def get_dt(self, response):
        dt = response.xpath("//meta[contains(@property, 'article:modified_time')]/@content").get()
        dt = self.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
        return dt