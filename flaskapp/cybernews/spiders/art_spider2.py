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
import sys

sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
import pws


converter = html2text.HTML2Text()
converter.ignore_links = True


class FCWArt(NewsSpider):
    name = "FCWArt"
    source = "FCW"
        
    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_dt(self, response):
        d = extract_text(response.css("li.date").get())
        dt = self.strptime(d, "%b %d, %Y")
        return dt

    def get_body(self, response):
        body = response.xpath(
            "//div[@id = 'article']/descendant::p[not(ancestor::div/@class='aboutAuthor')]"
        ).getall()
        body = [extract_text(para) for para in body]
        # check if first line is real text
        if len(body[0].split()) < 5:
            body = body[1:]
        return "\n\n".join(body)

    def get_tags(self, response):
        return None

    def get_title(self, response):
        return super().get_title(response, splitchar="--", splitchar2="--")


# TODO: handle weekends and yesterday's news after certain time.
class LawfareArt(NewsSpider):
    name = "LawfareArt"
    source = "Lawfare"

    baseurl = "https://www.lawfareblog.com"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_author(self, response):
        author = extract_text(response.css("div.article-top__contributors").get())
        return self.bycheck(author)

    def get_dt(self, response):
        d = extract_text(response.css("datetime").get())
        dt = self.strptime(d, "%A, %B %d, %Y")
        if not dt:
            dt = self.strptime(d, "%A, %B %d, %Y, %I:%M %p")
        return dt

    def get_body(self, response):
        # assume body of text is final element of class field-item
        return [extract_text(x) for x in response.css("div.field-items").getall()][-1]

    def get_tags(self, response):
        return [
            extract_text(tag)
            for tag in response.css("a[typeof='skos:Concept']").getall()
        ]



class InsideCSArt(NewsSpider):
    name = "ICSArt"
    source = "Inside Cybersecurity"
    baseurl = "https://insidecybersecurity.com"
    # start_urls = ["https://insidecybersecurity.com/daily-news"]


    def start_requests(self):
        url = "https://insidecybersecurity.com/daily-news"
        return scrapy.Request(url=url, callback=self.parse, headers=self.headers)


    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata=pws.InsideCS2,
            callback=self.logged_in,
            headers=self.headers,
            cb_kwargs=dict(dt=None),
        )

    # NOTE: CHANGING INSIDECS SIGNATURE - ADJUST REFERENCES ACCORDINGLY
    # TODO:change too handling all days after cutoff
    # NOTE: days filings are always done in the morning and weekends are skipped
    # Thus, current behavior only looking at today's stories should suffice
    def logged_in(self, response, dt):
        # get just todays content [0], confirm date within article, however
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.art_parse,
                headers=self.headers,
                cb_kwargs=dict(dt=dt, date_check=self.date_check),
            )

    # NOTE: old articles worked with this...
    # if this never works, turn get_dt2 into get_dt
    # for now, call get_dt2 upon failure.
    def get_dt(self, response):
        dt = extract_text(response.css(".timestamp").get()).strip()
        if not dt:
            return self.get_dt2(response)
        # check for trailing "|"
        if not (dt[-1].isdigit() or dt[-1].isalpha()):
            dt = dt[:-1].strip()
        return self.strptime(dt, "%B %d, %Y")

    # generic newsspider author returns format
    # "By Sara Friedmean / March 10, 2021"
    def get_dt2(self, response):
        dt = super().get_author(response).split("/")[1].strip()
        return self.strptime(dt, "%M %d, %Y")

    # see get_dt2 for format
    def get_author(self, response):
        return super().get_author(response).split("/")[0].strip()

    def get_title(self, response):
        return super().get_title(response, splitchar="|", splitchar2="|")

    def get_body(self, response):
        body = super().get_body(response)
        # check for "-" in trailing last 40 characters
        # as often aritcle ends with "- Author(contact@news.com)"
        if "-" in body[-40:]:
            body = body.split("-")[:-1]
            body = "-".join(body)
        return body


class CyberScoopArt(NewsSpider):
    name = "CyberScoopArt"
    source = "CyberScoop"
    
    def parse(self, response):
        self.art_parse( response, dt=None, date_check=self.date_check)

    def get_title(self, response):
        return extract_text(response.css(".article__title").get())

    def get_dt(self, response):
        dt = extract_text(response.css(".article__meta").get())
        dt = dt.lower().strip()
        if dt.endswith("| cyberscoop"):
            dt = dt[:-12].strip()
        dt = self.strptime(dt, "%b %d, %Y")
        return dt

    def get_body(self, response):
        # get all descendants of *usually div* with article__content-text label
        body = response.xpath("//*[@class = 'article__content-text']/descendant::p")
        body = self.join_body(body)
        return body

    def get_tags(self, response):
        return response.css(".tag-cloud-link::text").getall()

    def get_author(self, response):
        return extract_text(response.css(".article__author").get())


class WSJArt(NewsSpider):
    name = "WSJArt"
    source = "Wall Street Journal"
    start_urls = ["https://www.wsj.com/pro/cybersecurity"]


    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_title(self, response):
        return extract_text(response.css(".wsj-article-headline").get())

    # TODO: keep time of datetime object and make sure get_dt only passes dt object
    # and not str
    def get_dt(self, response):
        dt = response.css(".timestamp::text").get().strip()
        # last word is timezone; remove
        dt = " ".join(dt.split(" ")[:-1])
        dt = self.strptime(dt, "%b. %d, %Y %I:%M %p")
        if not dt:
            dt = self.strptime(dt, "%B %d, %Y %I:%M %p")
        return dt

    def get_author(self, response):
        if super().get_author(response):
            return super().get_author(response)
        else:
            return response.css(".name::text").get()
        # if author:
        #     return author
        # else:
        #     return response.xpath("//meta[@name='author']/@content").get()

    def get_body(self, response):
        # select p tags without class, or parent with print or email class
        # remove final p tag, which has author information
        body = response.xpath(
            """//p[not(@*) and 
            not(ancestor::*[contains(@class, 'print') 
                or contains(@class, 'email')])]"""
        )[:-1]
        # body = "\n".join([extract_text(para) for para in body.getall()])
        return self.join_body(body)


class SecAffArt(NewsSpider):
    source = "Security Affairs"
    name = "SecAffArt"
   
    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)


    def get_title(self, response):
        return extract_text(response.css(".post_title").get())

    def get_author(self, response):
        author = extract_text(response.css(".post_detail").get())
        return self.bycheck(author)

    # post_detail class in format "*date*... By *author*"
    def get_dt(self, response):
        dt = extract_text(response.css(".post_detail").get())
        dt = dt.split("By")[0].strip()
        return self.strptime(dt, "%B %d, %Y")

    def get_body(self, response):
        body = response.xpath("//p[not(ancestor::*[contains(@class, 'cli')])]")
        # remove tags that are empty; last three also are superflorous.
        body = [extract_text(b.get()) for b in body if extract_text(b.get())][:-3]
        return "\n\n".join(body)


class WiredArt(NewsSpider):
    source = "Wired"
    name = "WiredArt"
    baseurl = "https://www.wired.com"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_dt(self, response):
        dt = extract_text(
            response.xpath(
                "//time[contains(@data-testid, 'ContentHeaderPublishDate')]"
            ).get()
        )
        dt = self.strptime(dt, "%m.%d.%Y %I:%M %p")
        return dt

    def get_body(self, response):
        body = response.css("div.article__chunks").xpath(".//p")
        return self.join_body(body)

    def get_tags(self, response):
        # try using regex to extract tags, else fail gracefully
        # get "['a', 'b', ...]" after "tags:"
        pattern = re.compile(r"(?<=tags\":).*?\]")
        try:
            ls = response.xpath(
                "//script[contains(@type, 'text/javascript')]/text()"
            ).re(pattern)
            return json.load(ls[0])
        except:
            return None

    def get_title(self, response):
        return super().get_title(response, splitchar="|", splitchar2="|")


# TODO: check for expired dates in artparse
class DefenseOneArt(NewsSpider):
    name = "DefenseOneArt"
    source = "Defense One"

    # start_urls = ["https://www.defenseone.com/topic/cyber/"]
    baseurl = "https://www.defenseone.com"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)


    def get_title(self, response):
        title = super().get_title(response, splitchar="-", splitchar2="-")
        return title

    def get_author(self, response):
        if super().get_author(response):
            return super().get_author(response)
        title = extract_text(
            response.xpath("//p[contains(@class, 'content-byline')]").get()
        )
        return title
        # NOTE: there is one more option: gemg-author-link who's text needs to be run through by check

    def get_dt(self, response):
        dt = super().get_dt(response)
        dt = self.strptime(dt, "%B %d, %Y")
        return dt

    def get_tags(self, response):
        head = response.css("ul.content-topics")[0]
        tags = head.css("li.tags-item")
        tags = [extract_text(tag.get()) for tag in tags]
        return tags

    def get_body(self, response):
        body = response.xpath(
            """//p[not(@*) and 
            not(parent::div[contains(@class, 'survey-modal')])]"""
        )
        return self.join_body(body)


class ZDNetArt(NewsSpider):
    name = "ZDNetArt"
    source = "ZDNet"
    base_url = "https://www.zdnet.com/"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_dt(self, response):
        dt = response.xpath("//time/@datetime").get()
        dt = self.strptime(dt, "%Y-%m-%d %H:%M:%S")
        return dt

    def get_title(self, response):
        return super().get_title(response, "|", "|")

    def get_body(self, response):
        body = response.xpath("//div[@class='storyBody']/p")
        return self.join_body(body)


class C4ISRNETArt(NewsSpider):
    name = "C4ISRNETArt"
    source = "C4ISRNET"
    base_url = "https://www.c4isrnet.com"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_dt(self, response):
        dt = response.xpath(
            "//meta[contains(@property, 'published_time')]/@content"
        ).get()
        return self.strptime(dt, "%B %d, %Y %I:%M %p")

    def get_body(self, response):
        body = response.xpath("//article[contains(@itemprop, 'articleBody')]/p")
        return self.join_body(body)


class HillArt(NewsSpider):
    name = "TheHillArt"
    source = "The Hill"
    base_url = "https://thehill.com/"

    def parse(self, response):
        self.art_parse(response, dt=None, date_check=self.date_check)

    def get_dt(self, response):
        dt = extract_text(response.css("span.submitted-date").get())
        # remove trailing timezone characters
        dt = dt[:-4]
        return self.strptime(dt, "%m/%d/%y %I:%M %p")

    def get_title(self, response):
        return super().get_title(response, "|", "|")

    def get_tags(self, response):
        return response.css("div.article-tags").xpath(".//a/text()").getall()

    def get_body(self, response):
        body = response.css("div.field-items").xpath(".//p")
        return self.join_body(body)


# Bloomberg is tricker to scrap; skip for now
# class BloombergSpider(NewsSpider):
#     name = "Bloomberg"
#     start_urls = ["https://www.bloomberg.com/code-wars?sref=3OIZCXOE"]
