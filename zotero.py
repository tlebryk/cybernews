"""Utility functions for parsing results of zotero translation server"""

import requests
from datetime import datetime
from dateutil import parser


server = "https://arcane-meadow-07118.herokuapp.com/web"
headers = {"content-type": r"text/plain"}


def author_parse(cr):
    def concat_a(author):
        if author.get("name"):
            return author["name"]
        else:
            return author["firstName"] + " " + author["lastName"]
    author = ""
    if cr:
        author = author + concat_a(cr[0])
        if len(cr) == 2:
            author = author + " and " + concat_a(cr[1])
        elif len(cr) > 2:
            author += ", "
            for c in cr[1:-1]:
                author = author + concat_a(c) + ","
            author += " and "
            author = author + concat_a(c)
    return author


def get_meta(data, server=server, headers=headers):
    r = requests.post(server, data=data, headers=headers)
    if not r.ok:
        url = data
        title = ""
        author = ""
        source = ""
        date = ""
        body = ""
    else:
        d = r.json()[0]
        try:
            if d["itemType"] == "webpage":
                source = d["websiteTitle"]
            else:
                source = d["publicationTitle"]
        except:
            source = ""
        url = d["url"]

        dt = d.get("date")
        date = ""
        if dt:
            try:
                date = datetime.strptime(dt[:10], "%Y-%m-%d")
                date = datetime.strftime(date, "%B %d, %Y")
            except ValueError:
                try:
                    date = parser.parse(dt[:10])
                    date = datetime.strftime(date, "%B %d, %Y")
                except:
                    print("filler error")
        
        body = d.get("abstractNote")
        title = d.get("title")
        author = author_parse(d.get("creators"))

    item = {
        "url": str(url),
        "title": str(title),
        "author": str(author),
        "source": str(source),
        "date": str(date),
        "body": str(body),
    }
    print(item)
    return item


if __name__ == "__main__":
    # testing
    data = "https://www.washingtonpost.com/world/2021/05/04/mexico-city-metro-train-platform-collapse/"
    item = get_meta(data, server=server, headers=headers)
    print(item)