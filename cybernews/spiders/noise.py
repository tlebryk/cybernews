from . import dailyspider as DS
from . import articlesspider
from .newsspider import NewsSpider
import scrapy
from datetime import date, datetime, timedelta
import json
import sys
import urllib
sys.path.append("C:\\Users\\tlebr\\Google Drive\\fdd\\dailynews\\cybernews\\cybernews")
import oldarts


Spider = DS.InsideCS


class Noise(Spider):
    name = "Noise"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.break_flag = True
        self.source = super().name
        delta = self.latest - self.earliest
        self.days = [self.earliest + timedelta(days=i) for i in range(delta.days + 1)]
        self.start_urls = self.get_starturls()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, cb_kwargs=dict(date_check=False))

    def art_parse(self, response, dt=None, date_check=False):
        if response.url in self.recent_urls:
            return None
        x = super().art_parse(response, dt=dt, date_check=date_check)
        if x:
            x["Relevant"] = 0
            if x["date"]:
                if self.strptime(x["date"], "%Y-%b-%d %I:%M:%S") < self.earliest:
                    self.break_flag = False
                    print(f"{response.url}\n\n\n")
                    return None
        return x


class FCWNoise(Noise):
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
    def parse(self, response, cb=None):
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

class InsideCSNoise(Noise):
    name = "InsideCSNoise"

    def get_starturls(self):
        yield "https://insidecybersecurity.com/daily-news"

    def logged_in(self, response, dt=None, date_check=False):
        for i in range(8):
            url = f"https://insidecybersecurity.com/daily-news?page={i}"
            yield scrapy.Request(url=url,
                                 callback=super().logged_in,
                                 headers=self.headers,
                                 cb_kwargs={"date_check": date_check,
                                                 "dt": dt})


# NOTE: be careful with current breakflag behavior
class CyberScoopNoise(Noise):
    name = "CyberScoopNoise"

    def get_starturls(self):
        return None

    def start_requests(self):

        base = """https://www.cyberscoop.com/wp-admin/admin-ajax.php"""
        i = 0
        formdata = {
            "action": "loadmore",
            "query": """a:64:{s:14:"posts_per_page";i:10;s:11:"post_status";s:7:"publish";s:13:"category_name";s:10:"government";s:12:"post__not_in";a:1:{i:0;i:54942;}s:5:"error";s:0:"";s:1:"m";s:0:"";s:1:"p";i:0;s:11:"post_parent";s:0:"";s:7:"subpost";s:0:"";s:10:"subpost_id";s:0:"";s:10:"attachment";s:0:"";s:13:"attachment_id";i:0;s:4:"name";s:0:"";s:8:"pagename";s:0:"";s:7:"page_id";i:0;s:6:"second";s:0:"";s:6:"minute";s:0:"";s:4:"hour";s:0:"";s:3:"day";i:0;s:8:"monthnum";i:0;s:4:"year";i:0;s:1:"w";i:0;s:3:"tag";s:0:"";s:3:"cat";i:3;s:6:"tag_id";s:0:"";s:6:"author";s:0:"";s:11:"author_name";s:0:"";s:4:"feed";s:0:"";s:2:"tb";s:0:"";s:5:"paged";i:0;s:8:"meta_key";s:0:"";s:10:"meta_value";s:0:"";s:7:"preview";s:0:"";s:1:"s";s:0:"";s:8:"sentence";s:0:"";s:5:"title";s:0:"";s:6:"fields";s:0:"";s:10:"menu_order";s:0:"";s:5:"embed";s:0:"";s:12:"category__in";a:0:{}s:16:"category__not_in";a:0:{}s:13:"category__and";a:0:{}s:8:"post__in";a:0:{}s:13:"post_name__in";a:0:{}s:7:"tag__in";a:0:{}s:11:"tag__not_in";a:0:{}s:8:"tag__and";a:0:{}s:12:"tag_slug__in";a:0:{}s:13:"tag_slug__and";a:0:{}s:15:"post_parent__in";a:0:{}s:19:"post_parent__not_in";a:0:{}s:10:"author__in";a:0:{}s:14:"author__not_in";a:0:{}s:19:"ignore_sticky_posts";b:0;s:16:"suppress_filters";b:0;s:13:"cache_results";b:1;s:22:"update_post_term_cache";b:1;s:19:"lazy_load_term_meta";b:1;s:22:"update_post_meta_cache";b:1;s:9:"post_type";s:0:"";s:8:"nopaging";b:0;s:17:"comments_per_page";s:2:"50";s:13:"no_found_rows";b:0;s:5:"order";s:4:"DESC";}""",
            "page": str(i),
            "content": "news",
            "category_news": "government",
        }
        # currently 250 pages on government page as worst case cap
        while i < 6 and self.break_flag:
            formdata["page"] = str(i)
            yield scrapy.FormRequest(
                url=base, formdata=formdata, method="POST", callback=self.parse
            )
            i += 1

    def parse(self, response):
        x = response.css("a.article-thumb__title ::attr(href)")
        for url in x:
            yield scrapy.Request(url.get(), callback=self.art_parse)

    def art_parse(self, response, dt=None, date_check=False):
        x = super().art_parse(response, dt=dt, date_check=date_check)
        if x:
            if self.strptime(x["date"], "%Y-%b-%d %I:%M:%S") < self.earliest:
                self.break_flag = False
                print(response.url)
        return x


class WSJSpiderNoise(Noise):
    name = "WSJNoise"

    def get_starturls(self):
        return ["https://www.wsj.com/pro/cybersecurity/topics/public-sector-and-military?id=%7B%22site%22%3A%20%22Pro%20Cyber%22%2C%20%22topic%22%3A%20%22public-sector-and-military%22%2C%20%22params%22%3A%20%7B%20%22count%22%3A%2010%2C%20%22sort%22%3A%20%22date-desc%22%20%7D%2C%20%22clientId%22%3A%20%22grandcanyon%22%2C%20%22database%22%3A%20%22wsjpro%2Cwsjie%22%7D&type=dnsasearch_topics", 
        "https://www.wsj.com/pro/cybersecurity/topics/nation-states?id=%7B%22site%22%3A%20%22Pro%20Cyber%22%2C%20%22topic%22%3A%20%22nation-states%22%2C%20%22params%22%3A%20%7B%20%22count%22%3A%2010%2C%20%22sort%22%3A%20%22date-desc%22%20%7D%2C%20%22clientId%22%3A%20%22grandcanyon%22%2C%20%22database%22%3A%20%22wsjpro%2Cwsjie%22%7D&type=dnsasearch_topics"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.get_ids, headers=self.headers)
            
    # extracts topic between "topic" and "?"
    def get_topic(self, url):
        ind = url.find("topics/") + len('topics/')
        substr = url[ind:]
        end = substr.find("?")
        topic = url[ind:ind+end]
        return topic

    def get_ids(self, response):
        topic = self.get_topic(response.url)
        data = response.css("p::text").get()
        data = json.loads(data)
        ids = [el['id'] for el in data['collection']]
        for i in ids:
                url = f"https://www.wsj.com/pro/cybersecurity/topics/{topic}?id={i}&type=article%7Cdnsa"
                yield scrapy.Request(url, callback=self.get_url, headers=self.headers)
        
    def get_url(self, response):  
        data = response.css("p::text").get()
        data = json.loads(data)
        url = data['data']['url']
        return scrapy.Request(url, callback=self.art_parse, headers=self.headers)    

class SecAffNoise(Noise):
    name = "SecurityAffairsNoise"

    # TODO: build in functionality later to iterate through variable pages;
    # for now only go through 2 pages. 
    def get_starturls(self):
        for i in range(1,3):
            yield f"https://securityaffairs.co/wordpress/category/cyber-warfare-2/page/{i}"

class WiredNoise(Noise):
    name = 'WiredNoise'

    # TODO: build in functionality later to iterate through variable pages;
    # for now only go through 5 pages. 
    def get_starturls(self):
        for i in range(1,6):
            yield f"https://www.wired.com/category/security/page/{i}"

# TODO: ignore scrolling for now 
# articles on first page go to december 2020 anyway as of 3/22/2021
# scrolling requires querying based on timestamp of last loaded article
class DefenseOneNoise(Noise):
    name = "DefenseOneNoise"

    def get_starturls(self):
        yield "https://www.defenseone.com/topic/cyber/"

#  loading more should come from 
# /api/component/listing/eb8801ee-85ee-4a34-8b5f-ffc84778491a/content/4b71f49e-561e-43b0-a8e2-c6a588fe538d
# followed by lastassetid
#  for now run everyday and change overwrite flag to append in noiserunner.py
class ZDNetNoise(Noise):
    name = "ZDNetNoise"

    def get_starturls(self):
        yield "https://www.zdnet.com/topic/security/"

class C4ISRNETNoise(Noise):
    name = "C4ISRNETNoise"
    def get_starturls(self):
        yield "https://www.c4isrnet.com/cyber/?source=dfn-nav"


class HillNoise(Noise):
    name = "HillNoise"
    def get_starturls(self):
            for i in range(0,7):
                yield f"https://thehill.com/policy/cybersecurity?page={i}"


    # for c4isnetnoise headers
    # def scroll(self, scrolloffset):

        # body = {
        #     'contentConfig':  {"_jge":"content-feed",
        #         "Feed-Parameter":"/cyber",
        #         "Feed-Limit":"10",
        #         f"Feed-Offset":'{scrolloffset}'},

        #     'customFields': {"artworkPosition":"right",
        #         "offset":"0",
        #         "commentsCountCivil":"false",
        #         "showAuthor":"true",
        #         "showDate":"true",
        #         "commentsCountDisqus":"false",
        #         "numItems":"11",
        #         "formattingOption":"relative",
        #         "enabledLoadMore":"true",
        #         "showDescription":"true",
        #         "dateType":"displayOnly",
        #         "showdate":"true"}
        # }
        # body = urllib.parse.urlencode(body)

        # headers2 = {':authority': 'www.c4isrnet.com',
        #    ' :method': 'GET',
        #     ':path': '/pb/api/v2/render/feature/global/mco-results-list-load-more?contentConfig=%7B%22_jge%22%3A%22content-feed%22%2C%22Feed-Parameter%22%3A%22%2Fcyber%22%2C%22Feed-Limit%22%3A%2210%22%2C%22Feed-Offset%22%3A20%7D&customFields=%7B%22artworkPosition%22%3A%22right%22%2C%22offset%22%3A%220%22%2C%22commentsCountCivil%22%3A%22false%22%2C%22showAuthor%22%3A%22true%22%2C%22showDate%22%3A%22true%22%2C%22commentsCountDisqus%22%3A%22false%22%2C%22numItems%22%3A%2211%22%2C%22formattingOption%22%3A%22relative%22%2C%22enabledLoadMore%22%3A%22true%22%2C%22showDescription%22%3A%22true%22%2C%22dateType%22%3A%22displayOnly%22%2C%22showdate%22%3A%22true%22%7D&service=content-feed',
        #     ':scheme': 'https',
        #     'accept': '*/*',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'en-US,en;q=0.9',
        #     'cookie': '_admrla=2.2-e3fdcebe61ca3b93-9b74ad26-87ed-11eb-893c-d06fafae035f; sailthru_content=9ad2c96ae3b14f0f67349d3ab410bbcda69c3d25b06902630b4389d5cc859bb9; sailthru_visitor=b3d47a3c-02d0-4693-b8f5-8fb11ea8e4af; _awl=2.1616164464.0.4-f39ba827-e028cc772d81bf8eaf2313987d9f5adc-6763652d75732d6561737431-6054b66b-3; AKA_A2=A',
        #     'dnt': '1',
        #     'referer': 'https://www.c4isrnet.com/cyber/?source=dfn-nav',
        #     'sec-fetch-dest': 'empty',
        #     'sec-fetch-mode': 'cors',
        #     'sec-fetch-site': 'same-origin',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57',
        #     'x-requested-with': 'XMLHttpRequest'}

        # self.header.update(headers2)

        # yield scrapy.Request(url= "https://www.c4isrnet.com/pb/api/v2/render/feature/global/mco-results-list-load-more",
        #     body=body,
        #     header=self.headers,
        #     callback=self.parse)

# headers = {'sec-fetch-dest': 'empty',
# 'sec-fetch-mode': 'cors',
# 'sec-fetch-site': 'same-origin',
# 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54',
# 'x-requested-with': 'XMLHttpRequest',
# 'cookie': '''arrowImp=true; _mfuuid_=d244daad-df20-4bfc-b74c-7bb267446c5d; s_vi=[CS]v1|3025CB951A90C093-40000DFFE2F53F41[CE]; s_ecid=MCMID|06021395765587738241304386274121336651; chsn_cnsnt=tglr_ref,tglr_req,tglr_sess_id,tglr_sess_count,tglr_anon_id,tglr_tenant_id,tglr_virtual_ref,tglr_transit_id,chsn_dcsn_cache,pmpdid,pmpredirected,pmpredir,fuseid,cohsn_xs_id,hashID,etagID,reinforcedID,httpOnlyID,fpID,flID; tglr_tenant_id=src_1kYsAcdpfzbZ8UlNLYht1RPg3m2; tglr_anon_id=415c9f26-7071-47d9-9e26-7efceeb16961; cohsn_xs_id=697a2167-9f32-4660-a4e4-ec635885d108; aam_uuid=05800321741723164721318875839442321971; aamgam=segid=16845565,1413208,1413208; b2b-aam-segments=t=Innovation; fly_geo={"countryCode": "us"}; fly_device=desktop; tglr_sess_count=2; s_vnum=1618666014453&vn=2; upid_899602627=1; upid_233602613=1; s_getNewRepeat=1616164576467-Repeat; s_lv_zdnet=1616164576469; utag_main=v_id:017845847bed000c7fbbfc0b75fb03082002507a00bd0$_sn:2$_se:7$_ss:0$_st:1616166377231$vapi_domain:zdnet.com$ses_id:1616164455565;exp-session$_pn:2;exp-session$linktag:;exp-session; AMCV_10D31225525FF5790A490D4D@AdobeOrg=1585540135|MCMID|06021395765587738241304386274121336651|MCAID|3025CB951A90C093-40000DFFE2F53F41|MCOPTOUT-1616172021s|NONE|vVersion|4.4.0|MCIDTS|18705; fly_preferred_edition=us; fly_default_edition=us; zdnetSessionStarted=true; zdnetSessionCount=9; adblock_status=is_adblocking; upid_74008240=1; upid_116637478=1; upid_411151130=1; upid_67531012=1; OptanonConsent=isIABGlobal=false&datestamp=Sat+Mar+20+2021+00:18:50+GMT-0400+(Eastern+Daylight+Time)&version=6.7.0&hosts=&consentId=aebbbcb6-4c03-4ad2-9255-613e86140a1f&interactionCount=1&landingPath=NotLandingPage&groups=C0001:1,C0002:1,C0003:1,C0004:1&AwaitingReconsent=false&geolocation=US;VA; OptanonAlertBoxClosed=2021-03-20T04:18:50.246Z; viewGuid=6999b9fe-e9a1-4723-ae17-3259456fcefe; arrowImpCnt=29; upid_632301346=1'''}


# class InsideCSNoise(Noise):
#     name = "InsideCS_noise"
#     source = "InsideCS"

#     # call login once, then after that assume logged in
#     def get_starturls(self):
#         url = "https://insidecybersecurity.com/daily-news"
#         yield scrapy.Request(url, callback=parse)
