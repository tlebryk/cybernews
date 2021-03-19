from . import dailyspider as DS
from . import articlesspider
from .newsspider import NewsSpider
import scrapy
from datetime import date, datetime, timedelta
import sys

sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
import oldarts


Spider = DS.CyberScoop


class Noise(Spider):
    name = "Noise"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        delta = self.latest - self.earliest
        self.days = [self.earliest + timedelta(days=i) for i in range(delta.days + 1)]
        self.start_urls = self.get_starturls()

    def art_parse(self, response, dt=None, date_check=True):
        if response.url in self.recent_urls:
            return None
        x = super().art_parse(response, dt=dt, date_check=date_check)
        if x: 
            x["Relevant"] = 0
        return x


class FCWNoise(Noise):
    name = "FCW_Noise"
    source = "FCW"
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
    def parse(self, response, cb = None):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.insider_arts,
                headers=self.headers,
                cb_kwargs=dict(cb={"date_check": False}),
            )

    def art_parse(self, response, dt=None, date_check=False):
        if response.url in self.recent_urls:
            return None
        x = super().art_parse(response, dt=dt, date_check=date_check)
        x["Relevant"] = 0
        return x


# data path: "C:\Users\tlebr\Google Drive\fdd\dailynews\cybernews\data\fcwnoise.json"

# to do: break when earlier than earliest
class LawfareNoise(Noise):
    name = "Lawfare_noise"
    source = "Lawfare"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cutoff = self.earliest

    def get_starturls(self):
        start_urls = self.start_urls
        ls = []
        for i in range(5):
            ls.append(start_urls[0] + f"/?page={i}")
        return ls

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=self.headers,
                cb_kwargs=dict(cb={"date_check": False}),
            )


class CyberScoopNoise(Noise):
    name = "CyberScoopNoise"
    break_flag = True

    def get_starturls(self):
        return None

    def start_requests(self):
        
        base = '''https://www.cyberscoop.com/wp-admin/admin-ajax.php'''
        i=0
        formdata = {
            'action': 'loadmore',
            'query': '''a:64:{s:14:"posts_per_page";i:10;s:11:"post_status";s:7:"publish";s:13:"category_name";s:10:"government";s:12:"post__not_in";a:1:{i:0;i:54942;}s:5:"error";s:0:"";s:1:"m";s:0:"";s:1:"p";i:0;s:11:"post_parent";s:0:"";s:7:"subpost";s:0:"";s:10:"subpost_id";s:0:"";s:10:"attachment";s:0:"";s:13:"attachment_id";i:0;s:4:"name";s:0:"";s:8:"pagename";s:0:"";s:7:"page_id";i:0;s:6:"second";s:0:"";s:6:"minute";s:0:"";s:4:"hour";s:0:"";s:3:"day";i:0;s:8:"monthnum";i:0;s:4:"year";i:0;s:1:"w";i:0;s:3:"tag";s:0:"";s:3:"cat";i:3;s:6:"tag_id";s:0:"";s:6:"author";s:0:"";s:11:"author_name";s:0:"";s:4:"feed";s:0:"";s:2:"tb";s:0:"";s:5:"paged";i:0;s:8:"meta_key";s:0:"";s:10:"meta_value";s:0:"";s:7:"preview";s:0:"";s:1:"s";s:0:"";s:8:"sentence";s:0:"";s:5:"title";s:0:"";s:6:"fields";s:0:"";s:10:"menu_order";s:0:"";s:5:"embed";s:0:"";s:12:"category__in";a:0:{}s:16:"category__not_in";a:0:{}s:13:"category__and";a:0:{}s:8:"post__in";a:0:{}s:13:"post_name__in";a:0:{}s:7:"tag__in";a:0:{}s:11:"tag__not_in";a:0:{}s:8:"tag__and";a:0:{}s:12:"tag_slug__in";a:0:{}s:13:"tag_slug__and";a:0:{}s:15:"post_parent__in";a:0:{}s:19:"post_parent__not_in";a:0:{}s:10:"author__in";a:0:{}s:14:"author__not_in";a:0:{}s:19:"ignore_sticky_posts";b:0;s:16:"suppress_filters";b:0;s:13:"cache_results";b:1;s:22:"update_post_term_cache";b:1;s:19:"lazy_load_term_meta";b:1;s:22:"update_post_meta_cache";b:1;s:9:"post_type";s:0:"";s:8:"nopaging";b:0;s:17:"comments_per_page";s:2:"50";s:13:"no_found_rows";b:0;s:5:"order";s:4:"DESC";}''',
            'page': str(i),
            'content': 'news',
            'category_news': 'government'
        }
        # currently 250 pages on government page as worst case cap
        while i < 6 and self.break_flag:
            formdata['page'] = str(i)
            yield scrapy.FormRequest(url=base, formdata=formdata, method="POST", callback=self.parse)
            i+=1

    def parse(self, response):
        x=response.css("a.article-thumb__title ::attr(href)")
        for url in x:
            yield scrapy.Request(url.get(), callback=self.art_parse)

    def art_parse(self, response, dt=None, date_check=False):
        x = super().art_parse(response, dt=dt, date_check=date_check)
        if x:
            if self.strptime(x['date'], "%Y-%b-%d %I:%M:%S") < self.earliest: 
                self.break_flag = False
                print(response.url)
        return x

# class InsideCSNoise(Noise):
#     name = "InsideCS_noise"
#     source = "InsideCS"

#     # call login once, then after that assume logged in
#     def get_starturls(self):
#         url = "https://insidecybersecurity.com/daily-news"
#         yield scrapy.Request(url, callback=parse)
