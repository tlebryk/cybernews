import logging
from scrapy.utils.response import open_in_browser
from scrapy.shell import inspect_response
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
from .mideastspider import Kurd24Art

# # Password file not included  in repo.
# import sys
# sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
# import pws


converter = html2text.HTML2Text()
converter.ignore_links = True


class Kurd24Daily(Kurd24Art):
    # scrapy crawl Kurd24Daily -a cutoff="2021-06-24"
    name = "Kurd24Daily"
    source = "Kurdistan 24"
    start_urls = [
        "https://www.kurdistan24.net/en/category/politics/country/kurdistan",
        "https://www.kurdistan24.net/en/preparation/analysis",
    ]
    daily = True
    date_check = True
    urls_scrapped = set()

    # def __init__(self, *args, **kwargs):
    #     path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
    #     df2 = pd.read_excel(path2)
    #     kurd24 = df2[df2.Source.str.lower().str.strip() == "kurdistan 24"]
    #     kurd24 = kurd24[kurd24.Url.notna()]
    #     self.start_urls = [str(url) for url in list(kurd24.Url)]
    #     self.date_check = False
    #     self.articles = []
        # self.logger.info(f"before init: {self.cutoff}")
        # super().__init__(*args, **kwargs)
        # self.logger.info(f"after init: {self.cutoff}")

    def parse(self, response):
        # inspect_response(response, self)
        divs = response.css("div.col-sm-4.Most-read-boxes")
        for div in divs:
            url = div.css("a::attr(href)")[2].get()
            if url in self.urls_scrapped:
                self.logger.info(f"Continuing: Duplicate found duplicate url: {url}")
                continue
            else: 
                dt = extract_text(div.css("span.clock-share").get())
                dt = self.strptime(dt)
                if dt and self.date_check:
                    if not self.cutoff_check(url, dt):
                        break
                yield scrapy.Request(url, callback=self.art_parse, headers=self.headers)
                self.urls_scrapped.add(url)
                # check if article past cutoff date and stop collecting.



# class ReutersArt(NewsSpider):
#     # todo: get paywall arguments

#     name = "ReutersArt"
#     source = "Reuters"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def get_title(self, response, splitchar="|", splitchar2=None):
#         return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_dt(self, response):
#         dt = response.xpath("//meta[contains(@name, 'REVISION_DATE')]/@content").get()
#         dt = self.strptime(dt, "")
#         return dt

#     def get_body(self, response):
#         body = response.css("p.Paragraph-paragraph-2Bgue")
#         return self.join_body(body)

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         reuters = df2[df2.Source.str.lower().str.strip() == "reuters"]
#         reuters = reuters[reuters.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(reuters.Url)]
#         self.articles = []
#         super().__init__(*args, **kwargs)
#         # self.date_check = False

#     def parse(self, response):
#         return self.art_parse(response, dt=None, date_check=self.date_check)


# class AlmontArt(NewsSpider):
#     name = "AlmontArt"
#     source = "Al-monitor"

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "al-monitor"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         self.articles = []
#         super().__init__(*args, **kwargs)

#     def get_title(self, response, splitchar="-", splitchar2=None):
#         return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_author(self, response):
#         return extract_text(response.css("div.author-title").get())

#     def get_body(self, response):
#         return extract_text(response.css("div.field--name-body").get())

#     def get_tags(self, response):
#         tags = response.css("div.topic").getall()
#         tags = [extract_text(tag) for tag in tags]
#         return tags


# class SPGlobalArt(NewsSpider):
#     name = "SPGlobalArt"
#     source = "S&P Global Platts"

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "s&p global platts"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def get_tags(self, response):
#         tags = response.xpath("//meta[contains(@property, 'commodity')]/@content").get()
#         tags = tags.split("|")
#         return tags

#     def get_author(self, response):
#         return response.xpath("//a[contains(@data-gtm-action, 'Author')]/text()").get()

#     def get_title(self, response, splitchar="|", splitchar2=None):
#         return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_dt(self, response):
#         dt = extract_text(response.css("li.meta-data__date").get())
#         # remove trailing timezone
#         dt = " ".join(dt.split(" ")[:-1])
#         dt = self.strptime(dt, "%d %b %Y | %H:%M")
#         return dt

#     def get_body(self, response):
#         body = response.css("div.article__content")
#         body = self.join_body(body)
#         return body


# class APArt(NewsSpider):
#     name = "APArt"
#     source = "AP News"

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "ap news"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def get_tags(self, response):
#         tags = response.css("li.tag")
#         tags = [extract_text(tag.get()) for tag in tags]
#         return tags

#     def get_author(self, response):
#         author = extract_text(response.css("span.Component-bylines-0-2-63").get())
#         return self.bycheck(author)

#     def get_title(self, response, splitchar=None, splitchar2=None):
#         return response.xpath(
#             "//h1[contains(@class, 'Component-heading')]/text()"
#         ).get()

#     def get_body(self, response):
#         return extract_text(response.css("div.Article").get())

#     def get_dt(self, response):
#         dt = response.xpath(
#             "//meta[contains(@property, 'article:modified_time')]/@content"
#         ).get()
#         dt = self.strptime(dt, "%Y-%m-%dT%H:%M:%SZ")
#         return dt


# class AlJazeeraArt(NewsSpider):
#     name = "AlJazeeraArt"
#     source = "Al Jazeera"

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "al jazeera"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def get_tags(self, response):
#         return super().get_tags(response)

#     def get_author(self, response):
#         return response.xpath("//meta[contains(@name, 'author')]/@content").get()

#     def get_title(self, response, splitchar=None, splitchar2=None):
#         return response.xpath("//meta[contains(@name, 'og:title')]/@content").get()

#     def get_body(self, response):
#         return extract_text(response.css("div.wysiwyg").get())
#         return super().get_body(response)

#     def get_dt(self, response):
#         return self.strptime(response.css("div.date-simple::text").get())


# class BloombergArt(NewsSpider):
#     name = "BloombergArt"
#     source = "Bloomberg"

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "bloomberg"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def start_requests(self):
#         self.headers = {
#             "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             "accept-encoding": "gzip, deflate, br",
#             "accept-language": "en-US,en;q=0.9",
#             "cache-control": "max-age=0",
#             # 'cookie': '_sp_krux=false; _sp_v1_uid=1:11:27483f21-440f-426d-98c1-4e9cd3fd519e; _sp_v1_csv=null; _sp_v1_opt=1:; _sp_v1_lt=1:; ccpaUUID=d3819e4c-93b2-4a24-996f-ea171d4e96be; dnsDisplayed=true; ccpaApplies=true; signedLspa=false; bbgconsentstring=req1fun1pad1; agent_id=8369933f-fce5-4090-bcbb-5a6243ab15b0; session_id=e7c63b16-b769-47eb-a6a9-e33f366ca2be; session_key=9db49dd3c9bf9ceb922b53523c8b5732241d6292; _pxvid=e97dc66f-8277-11eb-987d-0242ac120010; __stripe_mid=1d441f8f-1b70-4819-b15b-cf3a653e5a777ee0d3; bdfpc=004.4088181781.1616070345287; _scid=04d8b18a-a30b-400b-898c-6df3452ded5e; __tbc=%7Bjzx%7Dt_3qvTkEkvt3AGEeiiNNgHCL6JIxlql1sI-kVj243huHzY9hj2j3JdK6CphH7i1XwPhx8lhksyqEINDmBYFgJ0mOTELfXejmF1QibWdobg-hHOV4U4sle4FGvQSmlCQwjylU0Z664w9lha1BgkmqDg; _sctr=1|1616040000000; xbc=%7Bjzx%7D5s5MuL3rTnMC7NSIZfcnPOcogwlJ6efuhIr5BM7bL11cu2wfd_Vqmj1X52MrYrywjaU7KGaXyT0BHRedOTmCX9CMd4z34Gm8WEgGxAjpxh2Vw9uZnK5L3VhZhT-EaC2XuZuPdncnqxTvIdAacoGoC-Ts0ppRsWgLPq-LmNMH6V8q6fyqMV-bVpSqjkzgKDVg13xb5_huMF1rsjabSRObnPeabGTOyujyWVZs6UKA8i_Ky5IwEDu5GnutYhRHcpp07E3jh6FX7Mo-s4tO5lkPW52c1LU24IVHALHkNRYwdtT7skb432euA_6jIgeRo9PDsbJ6jaS2WdS7mcnbxe2k-Q; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbLKK83J0YlRSkVil4AlqmtrlXSGvrJYAB7rhbDrAAAA; gatehouse_id=f0f4b079-2041-4677-928d-05547743f971; bb_geo_info={"countryCode":"US","country":"US","cityId":"4758390","provinceId":"6254928","field_p":"34AF11","field_d":"verizon.net","field_mi":6,"field_n":"hf","trackingRegion":"US","cacheExpiredTime":1628537823045,"region":"US","fieldMI":6,"fieldN":"hf","fieldD":"verizon.net","fieldP":"34AF11"}|1628537823045; bb_geo_info={"country":"US","region":"US","cityId":"4758390","provinceId":"6254928","fieldP":"34AF11","fieldD":"verizon.net","fieldMI":6,"fieldN":"hf"}|1628537830506; _reg-csrf=s%3AqNYfn_e7gNIgUKEYxe_QcAkt.MovpQC97bcbANclULMwuTiITrmxQSLLxai2QJy%2FWrdY; _user-status=anonymous; _reg-csrf-token=6hFxJfMH-LL38jGZBRG5yKnnRO3NLAmkN_V8; pxcts=faad0661-f6bc-11eb-861d-4fa2a2efd7e5; _sp_v1_data=2:334565:1619293304:0:81:0:81:0:0:_:-1; consentUUID=ba869aea-5a5c-42a2-b012-656fcf72b9b7; _px3=c0934951055a6e727c6432e4f87ef7e6a6036d4deabe8e42198206c8b5194efb:Sj+FW/lwsbzQTcS5U8nqmqzBV0efmKsw2L0GSnrKdIias0vsm/857inGEX+mP9u0AlL5EP8COM1Iil+zbfjjYA==:1000:NP84IJ/YrfijtnzdaCkAroswX/IIqRSsKTAASEdT3amcOXDJEFP7t9sTMjTXQfGKHxv13cA+UB78isNN12tBAWfGwjyFue/lMKAN2khGSPcW0N/T+2BFxpKCAyTr6clIoo6x4XSraYujo42hkuaoABW3VgYFH1vpOVd5UHuh5BKycCqwqaYCr0qmUojQhi+p2JycSRZ4ln8cnLPBI4igwQ==; _px2=eyJ1IjoiZmExMzg1ODAtZjZiYy0xMWViLTlmZTktMDVmZmU4YzA1OTZhIiwidiI6ImU5N2RjNjZmLTgyNzctMTFlYi05ODdkLTAyNDJhYzEyMDAxMCIsInQiOjE2MjgyNTgwMDk0NjYsImgiOiIyYzJkMTE1MjJhYjg2NmE3NWIzNDgyYzkwYzRmYjVhZjQ3YzQ1NGQ4ZjI2YmNlMzM1NmMzNmNmOTQ4NzM2YmY3In0=; _pxde=dddeeea0fccbff2fc001ad9b86bc591035e6073d7e8eaf12165dd4cb7d18512f:eyJ0aW1lc3RhbXAiOjE2MjgyNTc3Nzk2MDAsImZfa2IiOjAsImlwY19pZCI6W119'
#             "dnt": "1",
#             "if-none-match": 'W/"5709c-EaIgkOz84sZP+4jVwKsICZ2FoEI"',
#             "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
#             "sec-ch-ua-mobile": "?0",
#             "sec-fetch-dest": "document",
#             "sec-fetch-mode": "navigate",
#             "sec-fetch-site": "none",
#             "sec-fetch-user": "?1",
#             "upgrade-insecure-requests": "1",
#             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62",
#         }
#         return super().start_requests()

#     def parse(self, response):
#         # self.logger.info("hit bloom parse")
#         # open_in_browser(response)
#         # inspect_response(response, self)
#         return super().parse(response)

#     def get_tags(self, response):
#         return super().get_tags(response)

#     def get_author(self, response):
#         author = extract_text(
#             response.css("address.lede-text-v2__byline").get()
#         ).replace("\n", " ")
#         return self.bycheck(author)

#     def get_title(self, response, splitchar=None, splitchar2=None):
#         return extract_text(response.css("h1.lede-text-v2__hed").get())

#     def get_body(self, response):
#         return extract_text(response.css("div.body-copy-v2").get())

#     def get_dt(self, response, **kwargs):
#         return super().get_dt(response, ignoretz=True)


# class RudawArt(NewsSpider):
#     name = "RudawArt"
#     source = "Rudaw"
#     # TODO: commment out later
#     custom_settings = {
#         "FEEDS": {
#             f"cybernews/data/{name}.csv": {
#                 "format": "csv",
#                 "encoding": "utf8",
#             }
#         }
#     }
#     headers = {
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Connection": "keep-alive",
#         "DNT": "1",
#         "Host": "www.rudaw.net",
#         "Sec-Fetch-Dest": "document",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Site": "none",
#         "Sec-Fetch-User": "?1",
#         "Sec-GPC": "1",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
#     }

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "rudaw"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)][-2:]
#         super().__init__(*args, **kwargs)

#     def start_requests(self):
#         return super().start_requests()

#     def parse(self, response):
#         # self.logger.info("hit bloom parse")
#         # open_in_browser(response)
#         # inspect_response(response, self)
#         return super().parse(response)

#     def get_tags(self, response):
#         return super().get_tags(response)

#     def get_author(self, response):
#         logging.info("hit author")
#         return extract_text(response.css("div.article-main__author").get())

#     def get_title(self, response, splitchar=None, splitchar2=None):
#         return response.xpath("//meta[contains(@property, 'og:title')]/@content").get()

#     def get_body(self, response):
#         # last line is copyright
#         body = response.css("p")[:-3]
#         body = self.join_body(body)
#         return body

#     def get_dt(self, response):
#         return self.strptime(extract_text(response.css("span.date").get()))


# class JPostArt(NewsSpider):
#     name = "JPostArt"
#     source = "The Jerusalem Post"
#     custom_settings = {
#         "FEEDS": {
#             f"data/{name}.csv": {
#                 "format": "csv",
#                 "encoding": "utf8",
#             }
#         }
#     }

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "the jerusalem post"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)][:2]
#         super().__init__(*args, **kwargs)

#     def parse(self, response):
#         # self.logger.info("hit bloom parse")
#         # open_in_browser(response)
#         # inspect_response(response, self)
#         return super().parse(response)

#     def get_tags(self, response):
#         return response.css("a.tag::text").getall()

#     def get_author(self, response):
#         author = super().get_author(response)
#         author = author.split("\n")[0]
#         author = author.title()
#         return author

#     def get_title(self, response, splitchar="-", splitchar2=None):
#         return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_body(self, response):
#         body = response.xpath(
#             "//div[contains(@class, 'article-inner-content') and not(self::script)]"
#         )
#         body = body.xpath(
#             ".//node()[not(ancestor-or-self::script) and not(ancestor-or-self::*[contains(@class, 'hide-for-premium')]) and not(ancestor-or-self::template)]"
#         )
#         body = self.join_body(body)
#         return body

#     def get_dt(self, response):
#         dt = extract_text(response.css("div.article-subline-name").get())
#         dt = self.strptime(dt, "")
#         return dt


# class ReliefWebArt(NewsSpider):
#     name = "ReliefWebArt"
#     source = "Relief Web"
#     custom_settings = {
#         "FEEDS": {
#             f"data/{name}.csv": {
#                 "format": "csv",
#                 "encoding": "utf8",
#             }
#         }
#     }

#     def parse(self, response):
#         # inspect_response(response, self)
#         return super().parse(response)

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "relief web"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def get_tags(self, response):
#         tags = response.css("dd.theme")
#         tags = tags.css("li")
#         tags = [extract_text(t.get()) for t in tags]
#         return tags

#     def get_author(self, response):
#         return ""

#     def get_title(self, response, splitchar=None, splitchar2=None):
#         return extract_text(response.xpath("//article/header/h2").get())
#         # return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_body(self, response):
#         body = response.css("div.content")
#         body = body.css("div.content")
#         body = body.css("p")
#         return self.join_body(body)

#     def get_dt(self, response):
#         return super().get_dt(response)


# class WaPoArt(NewsSpider):
#     name = "WaPoArt"
#     source = "The Washington Post"
#     custom_settings = {
#         "FEEDS": {
#             f"data/{name}.csv": {
#                 "format": "csv",
#                 "encoding": "utf8",
#             }
#         }
#     }
#     headers = {
#         "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "accept-encoding": "gzip, deflate, br",
#         "accept-language": "en-US,en;q=0.9",
#         "cache-control": "max-age=0",
#         # cookie: wp_devicetype=0; wp_ak_osn=1|20210505; wp_ak_v_v=0|20210407; rplampr=0a|20181213; wp_ak_v_m=0|20210519; wp_geo=US|VA|511|20146-20149|; wp_country=US; ak_bmsc=6BC8706FEBB4CC89F56DF95DEDC8426D~000000000000000000000000000000~YAAQQ2UzuHxqjnh7AQAAY5CaeAxIfx7Aa92ZIPibcyzdTTzhADrl9KnW58+F4XzWc01fvnXn47qOmCPzdxg2tXVyzIwNd6jsRGG0IRlLMc2FxUNK0PQaGuRPaQOw7shugB+fUEx/h6BItZQFyGv3j4kTaREnrazR6bF9+fLWFVvg1k4nZrduuh7NB5rQoaGaY9UvepTAgB3vlNwUXNOeP+bZOL0HNrFSSl7Vqf0I95/hrXVp9b8oP9ry15/xtf8ZYayWGVdKBPxhPnHLJ63x7l8qptlbzclVcsExRvm04YQimsn3iiQ2n3LfSvY79eRacWQQ4ViLaedzOedSJuM9+erEjq9eHZnwqgUNBYaYaKQ54HbEllt7+vRxRJW/1GhpTpuVs9wWplcTrHgJb0EGGBo=; rpisb=rBEAA2ElBMFNbAAfb8eCAg==; wp_ak_bt=1|20200518; wp_ak_bfd=1|20201222; wp_ak_pp=1|20210310; washpost_poe=true; akaas_magnet-test=1632408035~rv=96~id=6a68490ea8099ce6ba3207205e7d9783~rn=; wp_pwapi_ar="H4sIAAAAAAAA/13LsRXAIAgFwF2oUwgI+rONIk6QLs/d0+f6e2muSN8d4YAqC1Y1eHdEaF10v/TQTeyCzl4Kmwqdi5AaaWhDdwqXPZphz2qckV3/Tb2J0TkfB5l4am8AAAA="; wp_usp=1---; bm_sv=E6859BB465ECC6C1B05DCCAFE46813BE~lGtBJPEIxOseokHkftMth12xWxpKEc/QuGzpOJNxwFsh3fcJ80bcqwHeQT4fJ4iwkEURCmrNYigAeq/wVC+2VU8RFG8gRTZvWfmu7oD4GJs9PvJbivjArGnsMD9lkEJSK+5C4JqaufjX1RwScCGDHEu3ww/Lmkd+ISNQdzsXGqQ=
#         "dnt": "1",
#         "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-fetch-dest": "document",
#         "sec-fetch-mode": "navigate",
#         "sec-fetch-site": "same-origin",
#         "sec-fetch-user": "?1",
#         "upgrade-insecure-requests": "1",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78",
#     }

#     def __init__(self, *args, **kwargs):
#         path2 = r"C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\old_arts\Machine Learning Tool 1 (1).xlsx"
#         df2 = pd.read_excel(path2)
#         stories = df2[df2.Source.str.lower().str.strip() == "the washington post"]
#         stories = stories[stories.Url.notna()]
#         kwargs["start_urls"] = [str(url) for url in list(stories.Url)]
#         super().__init__(*args, **kwargs)

#     def parse(self, response):
#         # inspect_response(response, self)
#         return super().parse(response)

#     def get_tags(self, response):
#         return super().get_tags(response)

#     def get_author(self, response):
#         authors = response.xpath("//span[@data-sc-c='author']")[0]
#         authors = authors.xpath(".//*[contains(@data-qa, 'author-name')]")
#         authors = [extract_text(a.get()) for a in authors]
#         return authors

#     def get_title(self, response, splitchar="-", splitchar2=None):
#         return super().get_title(response, splitchar=splitchar, splitchar2=splitchar2)

#     def get_body(self, response):
#         body = response.css("div.article-body")
#         body = body.css("p.font--article-body")
#         return self.join_body(body)

#     def get_dt(self, response):
#         dt = extract_text(
#             response.xpath("//span[contains(@data-qa, 'display-date')]").get()
#         )
#         return self.strptime(dt)