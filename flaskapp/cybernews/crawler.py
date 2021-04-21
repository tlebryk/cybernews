from scrapy.crawler import CrawlerProcess
# TODO: fix path
import spiders/newspider 

outputfile = "output.json"
c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
    'FEED_FORMAT': 'json',
    'FEED_URI': outputfile,
})

c.crawl(FCW)
c.start()