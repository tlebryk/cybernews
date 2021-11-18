# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from app import db
from app.models import Articles
from datetime import date, datetime
import logging

TODAY = date.today()


class ScrapersPipeline:
    def open_spider(self, spider):
        self.ls = []

    def process_item(self, item, spider):
        logging.info(f"{item.get('title')}")
        self.ls.append(item)
        return item

    def close_spider(self, spider):
        arts = Articles.query.filter_by(briefingdate=TODAY)
        nextart = arts.first()
        # return the id of the first article added
        # or none if no articles in list
        start = None
        counter = 0
        if not nextart:
            class filler:
                id = 0
                prevart = None
                # firstflag = True

            nextart = filler()
            logging.info(
                "No articles found during add_article. Initializing today's linked list"
            )
        else:
            while nextart.prevart and counter < 1000:
                nextart = Articles.query.get(nextart.prevart)
                counter += 1
            logging.info(
                f"""nextartprevart:{nextart.prevart};
                nextartnextart:{nextart.nextart};
                nextartid: {nextart.id};
                nextarttitle: {nextart.title};"""
            )
        for i, art in enumerate(self.ls):
            article = Articles(
                url=art["url"],
                title=art["title"],
                authors=art["author"],
                body=art["body"],
                source=art["source"],
                artdate=art["date"],
                prevart=0,
                nextart=nextart.id,
                # ranking = ranking,
            )
            db.session.add(article)
            db.session.flush()
            db.session.refresh(article)
            # if nxtart:
            #     a = Articles.query.get(nxtart)
            #     a.prevart = article.id
            #     db.session.commit()
            logging.info(f"nextart prev art before: {nextart.prevart}")
            nextart.prevart = article.id
            logging.info(f"nextart prev art after: {nextart.prevart}")
            # if not nextart.get("firstflag"):
            # even if first article, only a postgres object will get committed.
            db.session.commit()
            logging.info(f"added article: {art}")
            # save id of first entry
            nextart = article
        # return item
