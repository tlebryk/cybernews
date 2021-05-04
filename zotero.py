import requests
from datetime import datetime

server = "http://127.0.0.1:1969/web"
headers = {"content-type": r"text/plain"}


def get_meta(data, server=server, headers=headers):
    r = requests.post(server, data=data, headers=headers)
    d = r.json()[0]
    if d['itemType'] == 'webpage':
        source = d['websiteTitle']
    else:
        source = d["publicationTitle"]
    url = d["url"]

    date = d.get("date")
    if date:
        date = datetime.strptime(date[:10], "%Y-%m-%d")
        date = datetime.strftime(date, "%B %d, %Y")
    body = d["abstractNote"]
    title = d["title"]
    author = ""
    cr = d["creators"]
    if len(cr) > 0:
        author = author + cr[0]["firstName"] + " " + cr[0]["lastName"]
    if len(cr) == 2:
        author = author + " and " + cr[1]["firstName"] + " " + cr[1]["lastName"]
    elif len(cr) > 2:
        author += ", "
        for c in cr[1:-1]:
            author = author + c["firstName"] + " " + c["lastName"]+ ","
        author += " and " 
        author = author + cr[-1]["firstName"] + " " + cr[-1]["lastName"]


    item = {
        "url": url,
        "title": title,
        "author": author,
        "source": source,
        "date": date,
        "body": body,
    }
    print(item)
    return item


if __name__ == "__main__":
    data = "https://www.washingtonpost.com/world/2021/05/04/mexico-city-metro-train-platform-collapse/"
    item = get_meta(data, server=server, headers=headers)
    print(item)