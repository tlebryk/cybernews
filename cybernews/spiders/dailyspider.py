# TODO: change settings to encode using utf-8 (which is what extract text uses)
# TODO: uncomment project root imports
import scrapy
from datetime import date, datetime, timedelta
from html_text import extract_text
import html2text
from urllib.parse import urljoin
from dateutil import parser
import re
import json
from .newsspider import NewsSpider
from . import art_spider2 as AS2
import sys
from scrapy.utils.project import get_project_settings

sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
import pws


converter = html2text.HTML2Text()
converter.ignore_links = True

settings = get_project_settings()
articles = []


class FCWDaily(AS2.FCWArt):
    name = "FCWDaily"
    source = "FCW"
    daily = True

    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://fcw.com/Home.aspx"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        insider = self.getfcwinsider(response)
        if insider:
            return scrapy.Request(
                url=insider, callback=self.insider_arts, headers=self.headers
            )

    # get daily insider from home page using todays date
    def getfcwinsider(self, response):
        lis = response.xpath("//li")
        for x in lis:
            d = x.css("span.date::text").get()
            d = self.strptime(d, "%m/%d/%Y")
            if d:
                if d >= self.cutoff:
                    if "fcw-insider" in x.xpath(".//a/@href").get():
                        return x.xpath(".//a/@href").get()
        return None

    # get todays articles from the insider
    def insider_arts(self, response, cb={"dt": None, "date_check": True}):
        # select header based on unique ID
        header = response.xpath('//*[@id="ph_pcontent1_0_ctl00_h3Title"]')
        # get all elements of same level in tree until next header (assume links are in h4 tags)
        arts = header.xpath(".//following-sibling::h4/a/@href").getall()
        for art in arts:
            yield scrapy.Request(
                url=art, callback=self.art_parse, headers=self.headers, cb_kwargs=cb
            )


class LawfareDaily(AS2.LawfareArt):
    name = "LawfareDaily"
    souce = "Lawfare"
    daily = True
    # custom_settings = settings
    baseurl = "https://www.lawfareblog.com"

    def start_requests(self):
        self.start_urls = [
            "https://www.lawfareblog.com/topic/cybersecurity",
            "https://www.lawfareblog.com/topic/cybersecurity-and-deterrence",
        ]
        self.date_check = True
        self.articles = []
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, cb={}):
        arts = response.xpath("//article")
        for art in arts:
            url = art.css("article::attr(about)").get()
            url = urljoin(self.baseurl, url)
            if self.in_urls(url):
                continue
            dt = (
                art.xpath(".//div[@class='submitted'][not(@class='username')]/text()")
                # articles have @class=username tag with author name which [-1] removes
                # first three chars afterwards are "&nbsp;" so remove with [3:]
                .getall()[-1][3:].strip()
            )
            dt = self.strptime(dt, "%a, %b %d, %Y, %I:%M %p")
            if dt:
                cb["dt"] = dt
                if self.cutoff_check(url=url, dt=dt):
                    yield scrapy.Request(
                        url=url,
                        callback=self.art_parse,
                        headers=self.headers,
                        cb_kwargs=cb,
                    )
                # articles are chronological so stop returning
                else:
                    break
            # if can't find date, parse article to be safe
            else:
                yield scrapy.Request(
                    url=url,
                    callback=self.art_parse,
                    headers=self.headers,
                    cb_kwargs=dict(dt=dt, date_check=self.date_check),
                )


class CyberScoopDaily(AS2.CyberScoopArt):
    name = "CyberScoop"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.cyberscoop.com/news/government/"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        y = response.css(".article-thumb")
        for el in y:
            # meta is a string of how many days ago the article was published
            # e.g. "1 week ago," "5 days ago" etc.
            meta = extract_text(el.css(".article-thumb__meta").get())
            # discard any article that is more than 4 days old
            words = ["6", "week"]
            if any([k in meta for k in words]):
                break
            url = el.css("a::attr(href)").get()
            if self.in_urls(url):
                continue
            yield scrapy.Request(
                url=url,
                callback=self.art_parse,
                headers=self.headers,
                cb_kwargs=dict(dt=None),
            )


class WSJSpiderDaily(AS2.WSJArt):
    name = "Wall Street Journal"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.wsj.com/pro/cybersecurity"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    # No article dates are provided so assume at most top 5 articles are relevant
    def parse(self, response):
        x = response.css(".WSJProTheme--headline_headline--2-Y-CYHt")
        urls = [el.css("a::attr(href)").get() for el in x[:5]]
        for url in urls:
            if self.in_urls(url):
                continue
            yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)


class SecAffDaily(AS2.SecAffArt):
    name = "Security Affairs"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = [
            "https://securityaffairs.co/wordpress/category/cyber-warfare-2"
        ]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, date_check=True):
        articles = response.css(".post_wrapper")
        for art in articles:
            dt = extract_text(
                art.xpath(".//*[contains(@class, 'post_detail')]/a").get()
            )
            dt = self.strptime(dt, "%B %d, %Y")
            if dt and date_check:
                if dt < self.cutoff:
                    break
            url = art.xpath(".//h3/a/@href").get()
            if self.in_urls(url):
                continue
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.art_parse,
                cb_kwargs=dict(dt=dt),
            )


class WiredDaily(AS2.WiredArt):
    name = "Wired"
    baseurl = "https://www.wired.com"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.wired.com/category/security/page/1/"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, date_check=True):
        articles = response.css(".archive-item-component__info")
        for article in articles:
            dt = extract_text(article.css("time").get())
            dt = self.strptime(dt, "%B %d, %Y")
            if dt and date_check:
                if dt < self.cutoff:
                    break
            url = urljoin(self.baseurl, article.xpath("a/@href").get())
            if self.in_urls(url):
                continue
            yield scrapy.Request(
                url=url,
                callback=self.art_parse,
                headers=self.headers,
                cb_kwargs=dict(dt=dt),
            )


# TODO: check for expired dates in artparse
class DefenseOneDaily(AS2.DefenseOneArt):
    name = "Defense One"
    baseurl = "https://www.defenseone.com"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.defenseone.com/topic/cyber/"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    # first article is in different format,
    # all other articles caught through "innerarts"
    def parse(self, response, date_check=True):
        url = response.xpath("//h1[contains(@class, 'top-story')]/a/@href").get()
        url = urljoin(self.baseurl, url)
        if not self.in_urls(url):
            dt = extract_text(
                response.xpath("//*[contains(@class, 'story-meta-date')]").get()
            )
            dt = self.strptime(dt, "%M %d, %Y")
            if dt:
                if dt < self.cutoff and date_check:
                    return None
                else:
                    yield scrapy.Request(
                        url=url,
                        callback=self.art_parse,
                        headers=self.headers,
                        cb_kwargs=dict(dt=dt),
                    )
            else:
                yield scrapy.Request(
                    url=url,
                    callback=self.art_parse,
                    headers=self.headers,
                    cb_kwargs=dict(dt=dt),
                )
        innerarts = response.css("div.river-item-inner")
        for art in innerarts:
            dt = art.css("time::text").get()
            dt = self.strptime(dt, "%M %d, %Y")
            if dt:
                if dt < self.cutoff and date_check:
                    break
                url = urljoin(self.baseurl, art.xpath(".//a/@href").get())
                if self.in_urls(url):
                    continue
                yield scrapy.Request(
                    url=url,
                    callback=self.art_parse,
                    headers=self.headers,
                    cb_kwargs=dict(dt=dt),
                )


class ZDNetDaily(AS2.ZDNetArt):
    name = "ZDNet"
    base_url = "https://www.zdnet.com/"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.zdnet.com/topic/security/"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, date_check=True):
        heading = response.xpath("//section[contains(@id, 'topic-river-latest')]")
        articles = heading.xpath(".//a[@class='thumb']/@href")
        for article in articles:
            url = article.get()
            url = urljoin(self.base_url, url)
            if self.in_urls(url):
                continue
            yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)


class C4ISRNETDaily(AS2.C4ISRNETArt):
    name = "C4ISRNET"
    base_url = "https://www.c4isrnet.com"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://www.c4isrnet.com/cyber/?source=dfn-nav"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, date_check=True):
        articles = response.css("div.m-headlineTease__info")
        for article in articles:
            url = article.xpath(".//a/@href").get()
            if self.in_urls(url):
                continue
            dt = extract_text(article.xpath(".//time").get()).strip()
            if "days" in dt and dt[0].isnumeric():
                dt = self.today - timedelta(int(dt[0]))
                if self.cutoff > dt and date_check:
                    break
            yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)


class HillDaily(AS2.HillArt):
    name = "The Hill"
    base_url = "https://thehill.com/"
    daily = True
    # custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://thehill.com/policy/cybersecurity"]
        self.date_check = True
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response, date_check=True):
        articles = response.xpath("//article")
        for article in articles:
            dt = extract_text(article.xpath(".//span[contains(@*, 'date')]").get())
            # remove trailing timezone characters
            dt = dt[:-4]
            dt = self.strptime(dt, "%m/%d/%y %I:%M %p")
            if dt and date_check:
                if dt < self.cutoff:
                    break
            url = article.xpath(".//@about").get()
            url = urljoin(self.base_url, url)
            if self.in_urls(url):
                continue
            yield scrapy.Request(
                url=url,
                callback=self.art_parse,
                headers=self.headers,
                cb_kwargs=dict(dt=dt),
            )


"""
The following two spiders are commented out or omitted because
they require passwords to access. If you have subscriptions, 
place your login information in pws.py as a dictionary
"""
# # InsideCS is a special case where InsideCSARt calls start_requests which calls parse which
# # logs in and renders daily news page
# # InsideCSart overrides on logged_in() and renders urls defined in start urls
# # We need to overwrite logged_in() to scrap the articles on daily news

# class InsideCSDaily(AS2.InsideCSArt):
#     name = "Inside Cybersecurity"
#     baseurl = "https://insidecybersecurity.com"
#     daily = True
    # custom_settings = settings


#     # TODO:change too handling all days after cutoff
#     def logged_in(self, response, dt=None, date_check=True):
#         # get just todays content [0], confirm date within article, however
#         articles = response.css(".view-content")[0].css("h2 a::attr(href)").getall()
#         for article in articles:
#             url = urljoin(self.baseurl, article)
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(
#                 url,
#                 callback=self.art_parse,
#                 headers=self.headers,
#                 cb_kwargs=dict(dt=dt, date_check=date_check),
#             )


# Bloomberg is tricker to scrap; skip for now
# class BloombergSpider(NewsSpider):
#     name = "Bloomberg"
#     start_urls = ["https://www.bloomberg.com/code-wars?sref=3OIZCXOE"]
