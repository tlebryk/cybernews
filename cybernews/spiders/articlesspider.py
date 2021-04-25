from .newsspider import NewsSpider
from . import dailyspider as DS
from . import art_spider2 as AS2

import scrapy
from urllib.parse import urlparse
import json
from scrapy.crawler import CrawlerProcess

# No pws file in repo so remove to allow to keep running
# import sys
# sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
# import pws


DICT_LS = []

# class with spider associated with a 
# domain name and all urls for that domain. 
class UrlClump:
    def __init__(self, Spider):
        self.Spider = Spider
        self._url_ls = list()

    def add_url(self, url, rating=None):
        self._url_ls.append(url)

    def pop_url(self):
        if self._url_ls:
            return self._url_ls.pop()
        return None

# Get host name of a url's domain to help with clumping
def url_host(url):
    host = urlparse(url).hostname
    if host[:4] == "www.":
        host = host[4:]
    return host


# returns dict of UrlClumps
# where keys are host domain names and values are UrlClumps 
def sort_urls2(urls, Clumpdct={}):

    roots = {
        "fcw.com": AS2.FCWArt,
        "lawfareblog.com": AS2.LawfareArt,
        "cyberscoop.com": AS2.CyberScoopArt,
        "wsj.com": AS2.WSJArt,
        "c4isrnet.com": AS2.C4ISRNETArt,
        "defenseone.com": AS2.DefenseOneArt,
        "wired.com": AS2.WiredArt,
        "zdnet.com": AS2.ZDNetArt,
        "securityaffairs.co": AS2.SecAffArt,
        "thehill.com": AS2.HillArt,
        # "bloomberg.com": AS2.BloombergSpiderArt,
        # "insidecybersecurity.com": AS2.InsideCSArt,
    }
    for i, url in enumerate(urls):
        host = url_host(url)
        if not Clumpdct.get(host):
            spider = roots.get(host)
            if spider:
                Clumpdct[host] = UrlClump(Spider=spider)
                Clumpdct[host].add_url(url)
        else:
            Clumpdct[host].add_url(url)
    return Clumpdct


# makes spiders for each host url and will crawl urls
# and append rating and relevant information to returned dict
def get_articles(urls, settings):
    Clumpdct = sort_urls2(urls)
    process = CrawlerProcess(settings)
    for v in Clumpdct.values():
        Spider = v.Spider

        class ArtSpider(Spider):
            def start_requests(self, *args, **kwargs):
                for tup in self.url_tups:
                    yield scrapy.Request(
                        url=tup[0],
                        callback=self.parse2,
                        headers=self.headers,
                        cb_kwargs={"rating": tup[1], "filename": tup[2]},
                    )

            def parse2(self, response, rating, filename):
                result = self.art_parse(response, date_check=False)
                result["Rating"] = rating
                result["Filename"] = filename
                result["Relevant"] = 1
                DICT_LS.append(result)
                yield result
        # # add additional login for InsideCS when included
        # if Spider == DS.InsideCS:
        #     ArtSpider.start_urls = ["https://insidecybersecurity.com/daily-news"]
        #     ArtSpider.logged_in = ArtSpider.start_requests
        #     ArtSpider.start_requests = DS.InsideCS.start_requests
        process.crawl(ArtSpider, **{"url_tups": v._url_ls, "source": Spider.name})
    return process
