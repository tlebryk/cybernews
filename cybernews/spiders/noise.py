from . import dailyspider as DS
from . import articlesspider
from .newsspider import NewsSpider
import scrapy
from datetime import date, datetime, timedelta
import sys

sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
import oldarts




class FCWnoise(DS.FCW):
    name = "FCW_Noise"
    # years is list of strings with year
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        delta = self.latest - self.earliest
        self.days = [self.earliest + timedelta(days=i) for i in range(delta.days + 1)]
        self.start_urls = self.get_starturls()

    def get_starturls(self):
        prefix = "https://fcw.com/blogs/fcw-insider/"
        suffix = "topstories.aspx"
        ls = []
        for day in self.days:
            url = f"{prefix}{day.strftime('%Y')}/\
{day.strftime('%m')}/{day.strftime('%b%d')}{suffix}"
            ls.append(url)
        return ls

    # will ignore all filler days as non 200 code requests
    def parse(self, response):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.insider_arts,
                headers=self.headers,
                cb_kwargs=dict(cb={"date_check": False}),
            )

    def art_parse(self, response, dt=None, date_check=True):
        if response.url in self.recent_urls:
            return None
        x = super().art_parse(response, dt=dt, date_check=date_check)
        x["Relevant"] = 0
        return x
# data path: "C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\fcwnoise.json"