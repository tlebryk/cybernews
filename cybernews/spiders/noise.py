from . import dailyspider
from . import articlesspider
from .newsspider import NewsSpider


from .. import oldarts
from datetime import date, datetime, timedelta

earliest = date(2021, 2, 11)
latest = date.today()


class Noise(NewsSpider):
    name = "Noise"

    def __init__(self, urls):
        pass

    def art_parse(self, response, dt=None, date_check=True):
        d = super().art_parse(response, dt=None, date_check=True)
        d["Relevant"] = 0


class FCWnoise(NewsSpider):
    name = "FCW_Noise"
    # years is list of strings with year
    def __init__(self, earliest, latest, *a, **kw):
        delta = latest - earliest
        self.days = [earliest + timedelta(days=i) for i in range(delta.days + 1)]
        self.start_urls = self.get_starturls()
        super().__init__(*a, **kw)

    def get_starturls(self):
        prefix = "https://fcw.com/blogs/fcw-insider/"
        suffix = "topstories.aspx"
        ls = []
        for day in self.days:
            url = f"{prefix}{day.strftime('%Y')}/\
{day.strftime('%m')}/{day.strftime('%b%d')}{suffix}"
            ls.append(url)
        return ls

    def parse(self, response):
        for url in start_urls:
            yield Request(
                url=url,
                callback=self.insider_arts,
                headers=self.headers,
                cb_kwargs=dict(cb={"date_check": False}),
            )
