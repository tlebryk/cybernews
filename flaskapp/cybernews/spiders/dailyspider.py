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
settings["ITEM_PIPELINES"] = {
    'cybernews.pipelines.CyberNewsPipeline': 300
}

articles = []

class FCWDaily(AS2.FCWArt):
    name = "FCWDaily"
    source = "FCW"
    # daily marks this is daily spider for runner
    daily = True

    custom_settings = settings

    def start_requests(self):
        self.start_urls = ["https://fcw.com/Home.aspx"]
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        insider = self.getfcwinsider(response)
        if insider:
            return scrapy.Request(
                    url=insider, callback=self.insider_arts, headers=self.headers)

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


# TODO: handle weekends and yesterday's news after certain time.
class LawfareDaily(AS2.LawfareArt):
    name = "LawfareDaily"
    souce = "Lawfare"
    daily = True
    baseurl = "https://www.lawfareblog.com"

    def start_requests(self):
        # overwrite empty self.start_urls declared in NewSpider.init()
        self.start_urls = ["https://www.lawfareblog.com/topic/cybersecurity", 
                           "https://www.lawfareblog.com/topic/cybersecurity-and-deterrence"]
        self.date_check = True
        self.articles = []
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)


    def parse(self, response, cb={}):
        arts = response.xpath("//article")
        for art in arts:
            # articles have @class=username tag with author name which [-1] removes
            # first three chars afterwards are "&nbsp;" so remove with [3:]
            url = art.css("article::attr(about)").get()
            url = urljoin(self.baseurl, url)
            if self.in_urls(url):
                continue
            dt = (
                art.xpath(".//div[@class='submitted'][not(@class='username')]/text()")
                .getall()[-1][3:]
                .strip()
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



class InsideCSDaily(NewsSpider):
    name = "Inside Cybersecurity"
    baseurl = "https://insidecybersecurity.com"
    daily = True



    def start_requests(self):
        # overwrite empty self.start_urls declared in NewSpider.init()
        self.start_urls = ["https://insidecybersecurity.com/daily-news"]
        self.date_check = True
        self.articles = []
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers)
    # TODO:change too handling all days after cutoff
    # NOTE: days filings are always done in the morning and weekends are skipped
    # Thus, current behavior only looking at today's stories should suffice
    def logged_in(self, response, dt=None, date_check=True):
        # get just todays content [0], confirm date within article, however
        articles = response.css(".view-content")[0].css("h2 a::attr(href)").getall()
        for article in articles:
            url = urljoin(self.baseurl, article)
            if self.in_urls(url):
                continue
            yield scrapy.Request(
                url,
                callback=self.art_parse,
                headers=self.headers,
                cb_kwargs=dict(dt=dt, date_check=date_check),
            )

    def parse(self, response, date_check=True):
        return scrapy.FormRequest.from_response(
            response,
            formdata=pws.InsideCS2,
            callback=self.logged_in,
            headers=self.headers,
            cb_kwargs=dict(dt=None, date_check=date_check),
        )



# class CyberScoopDaily(NewsSpider):
#     name = "CyberScoop"
#     start_urls = ["https://www.cyberscoop.com/news/government/"]

#     def parse(self, response):
#         y = response.css(".article-thumb")
#         for el in y:
#             # meta is a string of how many days ago the article was published
#             # e.g. "1 week ago," "5 days ago" etc.
#             meta = extract_text(el.css(".article-thumb__meta").get())
#             # discard any article that is more than 4 days old
#             words = ["6", "week"]
#             # test placeholder; uncomment above line
#             # words = ["week"]
#             if any([k in meta for k in words]):
#                 break
#             url = el.css("a::attr(href)").get()
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(
#                 url=url,
#                 callback=self.art_parse,
#                 headers=self.headers,
#                 cb_kwargs=dict(dt=None),
#             )

#     def get_title(self, response):
#         return extract_text(response.css(".article__title").get())

#     def get_dt(self, response):
#         dt = extract_text(response.css(".article__meta").get())
#         dt = dt.lower().strip()
#         if dt.endswith("| cyberscoop"):
#             dt = dt[:-12].strip()
#         dt = self.strptime(dt, "%b %d, %Y")
#         return dt

#     def get_body(self, response):
#         # get all descendants of *usually div* with article__content-text label
#         body = response.xpath("//*[@class = 'article__content-text']/descendant::p")
#         body = self.join_body(body)
#         return body

#     def get_tags(self, response):
#         return response.css(".tag-cloud-link::text").getall()

#     def get_author(self, response):
#         return extract_text(response.css(".article__author").get())


# class WSJSpiderDaily(NewsSpider):
#     name = "Wall Street Journal"
#     start_urls = ["https://www.wsj.com/pro/cybersecurity"]

#     # No article dates are provided so assume at most top 5 articles are relevant
#     def parse(self, response):
#         x = response.css(".WSJProTheme--headline_headline--2-Y-CYHt")
#         urls = [el.css("a::attr(href)").get() for el in x[:5]]
#         for url in urls:
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)

#     def get_title(self, response):
#         return extract_text(response.css(".wsj-article-headline").get())

#     # TODO: keep time of datetime object and make sure get_dt only passes dt object
#     # and not str
#     def get_dt(self, response):
#         dt = response.css(".timestamp::text").get().strip()
#         # last word is timezone; remove
#         dt = " ".join(dt.split(" ")[:-1])
#         dt = self.strptime(dt, "%b. %d, %Y %I:%M %p")
#         if not dt:
#             dt = self.strptime(dt, "%B %d, %Y %I:%M %p")
#         return dt

#     def get_author(self, response):
#         if super().get_author(response):
#             return super().get_author(response)
#         else:
#             return response.css(".name::text").get()
#         # if author:
#         #     return author
#         # else:
#         #     return response.xpath("//meta[@name='author']/@content").get()

#     def get_body(self, response):
#         # select p tags without class, or parent with print or email class
#         # remove final p tag, which has author information
#         body = response.xpath(
#             """//p[not(@*) and 
#             not(ancestor::*[contains(@class, 'print') 
#                 or contains(@class, 'email')])]"""
#         )[:-1]
#         # body = "\n".join([extract_text(para) for para in body.getall()])
#         return self.join_body(body)


# class SecAffDaily(NewsSpider):
#     name = "Security Affairs"
#     start_urls = ["https://securityaffairs.co/wordpress/category/cyber-warfare-2"]

#     def parse(self, response, date_check=True):
#         articles = response.css(".post_wrapper")
#         for art in articles:
#             dt = extract_text(
#                 art.xpath(".//*[contains(@class, 'post_detail')]/a").get()
#             )
#             dt = self.strptime(dt, "%B %d, %Y")
#             if dt and date_check:
#                 if dt < self.cutoff:
#                     break
#             url = art.xpath(".//h3/a/@href").get()
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(
#                 url=url,
#                 headers=self.headers,
#                 callback=self.art_parse,
#                 cb_kwargs=dict(dt=dt),
#             )

#     def get_title(self, response):
#         return extract_text(response.css(".post_title").get())

#     def get_author(self, response):
#         author = extract_text(response.css(".post_detail").get())
#         return self.bycheck(author)

#     # post_detail class in format "*date*... By *author*"
#     def get_dt(self, response):
#         dt = extract_text(response.css(".post_detail").get())
#         dt = dt.split("By")[0].strip()
#         return self.strptime(dt, "%B %d, %Y")

#     def get_body(self, response):
#         body = response.xpath("//p[not(ancestor::*[contains(@class, 'cli')])]")
#         # remove tags that are empty; last three also are superflorous.
#         body = [extract_text(b.get()) for b in body if extract_text(b.get())][:-3]
#         return "\n".join(body)


# class WiredDaily(NewsSpider):
#     name = "Wired"
#     start_urls = ["https://www.wired.com/category/security/page/1/"]
#     baseurl = "https://www.wired.com"

#     def parse(self, response, date_check=True):
#         articles = response.css(".archive-item-component__info")
#         for article in articles:
#             dt = extract_text(article.css("time").get())
#             dt = self.strptime(dt, "%B %d, %Y")
#             if dt and date_check:
#                 if dt < self.cutoff:
#                     break
#             url = urljoin(self.baseurl, article.xpath("a/@href").get())
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(
#                 url=url,
#                 callback=self.art_parse,
#                 headers=self.headers,
#                 cb_kwargs=dict(dt=dt),
#             )

#     def get_dt(self, response):
#         dt = extract_text(
#             response.xpath(
#                 "//time[contains(@data-testid, 'ContentHeaderPublishDate')]"
#             ).get()
#         )
#         dt = self.strptime(dt, "%m.%d.%Y %I:%M %p")
#         return dt

#     def get_body(self, response):
#         body = response.css("div.article__chunks").xpath(".//p")
#         return self.join_body(body)

#     def get_tags(self, response):
#         # try using regex to extract tags, else fail gracefully
#         # get "['a', 'b', ...]" after "tags:"
#         pattern = re.compile(r"(?<=tags\":).*?\]")
#         try:
#             ls = response.xpath(
#                 "//script[contains(@type, 'text/javascript')]/text()"
#             ).re(pattern)
#             return json.load(ls[0])
#         except:
#             return None

#     def get_title(self, response):
#         return super().get_title(response, splitchar="|", splitchar2="|")


# # TODO: check for expired dates in artparse
# class DefenseOneDaily(NewsSpider):
#     name = "Defense One"
#     start_urls = ["https://www.defenseone.com/topic/cyber/"]
#     baseurl = "https://www.defenseone.com"
#     # first article is in different format,
#     # all other articles caught through "innerarts"
#     def parse(self, response, date_check=True):
#         url = response.xpath("//h1[contains(@class, 'top-story')]/a/@href").get()
#         url = urljoin(self.baseurl, url)
#         if not self.in_urls(url):
#             dt = extract_text(
#                 response.xpath("//*[contains(@class, 'story-meta-date')]").get()
#             )
#             dt = self.strptime(dt, "%M %d, %Y")
#             if dt:
#                 if dt < self.cutoff and date_check:
#                     return None
#                 else:
#                     yield scrapy.Request(
#                         url=url,
#                         callback=self.art_parse,
#                         headers=self.headers,
#                         cb_kwargs=dict(dt=dt),
#                     )
#             else:
#                 yield scrapy.Request(
#                     url=url,
#                     callback=self.art_parse,
#                     headers=self.headers,
#                     cb_kwargs=dict(dt=dt),
#                 )
#         innerarts = response.css("div.river-item-inner")
#         for art in innerarts:
#             dt = art.css("time::text").get()
#             dt = self.strptime(dt, "%M %d, %Y")
#             if dt:
#                 if dt < self.cutoff and date_check:
#                     break
#                 url = urljoin(self.baseurl, art.xpath(".//a/@href").get())
#                 if self.in_urls(url):
#                     continue
#                 yield scrapy.Request(
#                     url=url,
#                     callback=self.art_parse,
#                     headers=self.headers,
#                     cb_kwargs=dict(dt=dt),
#                 )

#     def get_title(self, response):
#         title = super().get_title(response, splitchar="-", splitchar2="-")
#         return title

#     def get_author(self, response):
#         if super().get_author(response):
#             return super().get_author(response)
#         title = extract_text(
#             response.xpath("//p[contains(@class, 'content-byline')]").get()
#         )
#         return title
#         # NOTE: there is one more option: gemg-author-link who's text needs to be run through by check

#     def get_dt(self, response):
#         dt = super().get_dt(response)
#         dt = self.strptime(dt, "%B %d, %Y")
#         return dt

#     def get_tags(self, response):
#         head = response.css("ul.content-topics")[0]
#         tags = head.css("li.tags-item")
#         tags = [extract_text(tag.get()) for tag in tags]
#         return tags

#     def get_body(self, response):
#         body = response.xpath(
#             """//p[not(@*) and 
#             not(parent::div[contains(@class, 'survey-modal')])]"""
#         )
#         return self.join_body(body)


# class ZDNetDaily(NewsSpider):
#     name = "ZDNet"
#     start_urls = ["https://www.zdnet.com/topic/security/"]
#     base_url = "https://www.zdnet.com/"

#     def parse(self, response, date_check=True):
#         heading = response.xpath("//section[contains(@id, 'topic-river-latest')]")
#         articles = heading.xpath(".//a[@class='thumb']/@href")
#         for article in articles:
#             url = article.get()
#             url = urljoin(self.base_url, url)
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)

#     def get_dt(self, response):
#         dt = response.xpath("//time/@datetime").get()
#         dt = self.strptime(dt, "%Y-%m-%d %H:%M:%S")
#         return dt

#     def get_title(self, response):
#         return super().get_title(response, "|", "|")

#     def get_body(self, response):
#         body = response.xpath("//div[@class='storyBody']/p")
#         return self.join_body(body)


# class C4ISRNETDaily(NewsSpider):
#     name = "C4ISRNET"
#     start_urls = ["https://www.c4isrnet.com/cyber/?source=dfn-nav"]
#     base_url = "https://www.c4isrnet.com"

#     def parse(self, response, date_check=True):
#         articles = response.css("div.m-headlineTease__info")
#         for article in articles:
#             url = article.xpath(".//a/@href").get()
#             if self.in_urls(url):
#                 continue
#             dt = extract_text(article.xpath(".//time").get()).strip()
#             if "days" in dt and dt[0].isnumeric():
#                 dt = self.today - timedelta(int(dt[0]))
#                 if self.cutoff > dt and date_check:
#                     break
#             yield scrapy.Request(url=url, callback=self.art_parse, headers=self.headers)

#     def get_dt(self, response):
#         dt = response.xpath(
#             "//meta[contains(@property, 'published_time')]/@content"
#         ).get()
#         return self.strptime(dt, "%B %d, %Y %I:%M %p")

#     def get_body(self, response):
#         body = response.xpath("//article[contains(@itemprop, 'articleBody')]/p")
#         return self.join_body(body)


# class HillDaily(NewsSpider):
#     name = "The Hill"
#     start_urls = ["https://thehill.com/policy/cybersecurity"]
#     base_url = "https://thehill.com/"

#     def parse(self, response, date_check=True):
#         articles = response.xpath("//article")
#         for article in articles:
#             dt = extract_text(article.xpath(".//span[contains(@*, 'date')]").get())
#             # remove trailing timezone characters
#             dt = dt[:-4]
#             dt = self.strptime(dt, "%m/%d/%y %I:%M %p")
#             if dt and date_check:
#                 if dt < self.cutoff:
#                     break
#             url = article.xpath(".//@about").get()
#             url = urljoin(self.base_url, url)
#             if self.in_urls(url):
#                 continue
#             yield scrapy.Request(
#                 url=url,
#                 callback=self.art_parse,
#                 headers=self.headers,
#                 cb_kwargs=dict(dt=dt),
#             )

#     def get_dt(self, response):
#         dt = extract_text(response.css("span.submitted-date").get())
#         # remove trailing timezone characters
#         dt = dt[:-4]
#         return self.strptime(dt, "%m/%d/%y %I:%M %p")

#     def get_title(self, response):
#         return super().get_title(response, "|", "|")

#     def get_tags(self, response):
#         return response.css("div.article-tags").xpath(".//a/text()").getall()

#     def get_body(self, response):
#         body = response.css("div.field-items").xpath(".//p")
#         return self.join_body(body)


# # Bloomberg is tricker to scrap; skip for now
# # class BloombergSpider(NewsSpider):
# #     name = "Bloomberg"
# #     start_urls = ["https://www.bloomberg.com/code-wars?sref=3OIZCXOE"]
