# TODO:
# 1. article editer
# 2. Article delete
# 3. article rerank


from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from forms import ArticleForm
import exportword
from datetime import date

app = Flask(__name__)

# filler; make environment variable later
app.config["SECRET_KEY"] = "6f1f6f1c724600453622f48c48555e73"

td = date.today()

# for testing purposes, prepopulate 2 articles
articles = [
    {
        "title": "filler",
        "author": "Sara Friedman",
        "body": """But nearly a dozen current and former officials familiar with the deliberations say that it has been the casualty of classic Washington dramas: executive branch officials wary of legislators meddling in their business and government bureaucrats trying to fend off potential colleagues from encroaching on their perceived portfolios.
    The failure to fill the role, which would be responsible for coordinating the entire U.S. government’s defensive cyber operations, comes as the new administration grapples with how to kick suspected Russian and Chinese hackers out of federal cyber infrastructure following two major breaches. And it lays bare the challenges in setting up a brand new agency that could encroach upon some power centers in the White House, particularly the National Security Council.
    Sen. Angus King (I-Maine), who serves as co-chairman of the Cyberspace Solarium Commission — the body that successfully pushed for the inclusion of the National Cyber Director role in last year’s National Defense Authorization Act — said he was “frustrated” by the delay.
    “It’s like we are in conflict and they are not appointing the secretary of defense,” he said. “I would hate to have another attack occur in the next 30-60 days and still not have anyone in that position.”
    The White House has indicat""",
        "url": "https://insidecybersecurity.com/daily-news/lawmakers-federal-officials-begin-examining-next-set-cyber-policy-needs-amid-covid-and",
        "source": "Inside Cybersecurity",
        "date": "March 2, 2021",
    },
    {
        "title": "filler2",
        "author": "Tonya Riley",
        "body": """ The attempted intrusions comes six months ahead of Germany’s national elections. The German parliament has been a recurring target for foreign hackers, including a 2015 breach that the European Union blamed on Russia’s military intelligence agency. Since the Russian hack-and-leak operation aimed at the 2016 U.S. election, governments around Europe have braced for similar interference efforts in their politics.
    The culprit in the latest attempts to snoop on German lawmakers is far from clear. German news outlet Tagesschau reported that a group dubbed Ghostwriter was responsible. Those attackers have a history of targeting people in Eastern Europe with information operations that further “Russian security interests,” cybersecurity firm FireEye has said. One of the more dramatic examples came in April 2020 when Polish officials suggested Russian hackers had planted a fake letter on the website of a Polish military academy critical of the U.S. military presence in Poland.
    FireEye has not attributed the Ghostwriter campaign to a known hacking group, and German authorities have not publicly identified a culprit for the activity. CyberScoop could not independently confirm that the Ghostwriter attackers were responsible.
    As a powerful member of the European Union, German government agencies and corporations regularly find themselves in the crosshairs of suspected Russian and Chinese espionage. Last year, German authorities uncovered evidence of “longstanding compromises” at German critical infrastructure companies at the hands of a Kremlin-linked hacking group, CyberScoop has reported.  """,
        "url": "https://www.cyberscoop.com/us-intelligence-report-warns-of-increased-offensive-cyber-disinformation-around-the-world/",
        "source": "CyberScoop",
        "date": "March 1, 2021",
    },
    {
        "title": "filler3",
        "author": "Tonya Riley",
        "body": """ The attempted intrusions comes six months ahead of Germany’s national elections. The German parliament has been a recurring target for foreign hackers, including a 2015 breach that the European Union blamed on Russia’s military intelligence agency. Since the Russian hack-and-leak operation aimed at the 2016 U.S. election, governments around Europe have braced for similar interference efforts in their politics.
    The culprit in the latest attempts to snoop on German lawmakers is far from clear. German news outlet Tagesschau reported that a group dubbed Ghostwriter was responsible. Those attackers have a history of targeting people in Eastern Europe with information operations that further “Russian security interests,” cybersecurity firm FireEye has said. One of the more dramatic examples came in April 2020 when Polish officials suggested Russian hackers had planted a fake letter on the website of a Polish military academy critical of the U.S. military presence in Poland.
    FireEye has not attributed the Ghostwriter campaign to a known hacking group, and German authorities have not publicly identified a culprit for the activity. CyberScoop could not independently confirm that the Ghostwriter attackers were responsible.
    As a powerful member of the European Union, German government agencies and corporations regularly find themselves in the crosshairs of suspected Russian and Chinese espionage. Last year, German authorities uncovered evidence of “longstanding compromises” at German critical infrastructure companies at the hands of a Kremlin-linked hacking group, CyberScoop has reported.  """,
        "url": "https://www.cyberscoop.com/us-intelligence-report-warns-of-increased-offensive-cyber-disinformation-around-the-world/",
        "source": "CyberScoop",
        "date": "March 1, 2021",
    },
]


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    # if request.method == "POST":
    #     exportword.cyber_export(f"docs/{td.strftime('%B_%d_%Y')}.docx", articles)
    return render_template("home.html", articles=articles)


# for testing purposes
@app.route("/printer", methods=["GET", "POST"])
def printer():
    for a in articles:
        print(a["title"])
    return render_template("home.html", articles=articles)


# TODO:
# 1. Make this Ajax
# 2. relayer buttons... all on same level?
@app.route("/export", methods=["POST"])
def background_export():
    if request.method == "POST":
        exportword.cyber_export(
            f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx", articles
        )
        flash(f"Exported: click download to download", "success")
    return render_template("home.html", articles=articles)


# TODO:
# 1. Make textbox larger
@app.route("/article_form", methods=["POST", "GET"])
def add_article():
    f = ArticleForm()
    if request.method == "POST":
        req = request.form.copy()
        req["body"] = req["body"].replace("\r", "")
        # always insert at end of list
        articles.append(req)
    if f.validate_on_submit():
        flash(f"Added {f.title.data}", "success")
        return redirect(url_for("home"))
    return render_template("article_form.html", form=f, legend="Create Post")


@app.route("/download", methods=["POST"])
def downloadFile():
    if request.method == "POST":
        path = f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx"
        return send_file(path, as_attachment=True)


# This way of finding and deleting is pretty degenerate...
@app.route("/post/<article_title>/delete_post", methods=["POST"])
def delete_post(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
    
    i,_ = a
    articles.pop(i)
    return redirect(url_for("home"))


@app.route("/post/<article_title>/update", methods=["POST", "GET"])
def update_post(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i, a = a
    f = ArticleForm()
    if request.method == "GET":
        f.title.data = a.get("title")
        f.body.data = a.get("body")
        f.url.data = a.get("url")
        f.source.data = a.get("source")
        f.author.data = a.get("author")
        f.date.data = a.get("date")
    if request.method == "POST":
        req = request.form.copy()
        req["body"] = req["body"].replace("\r", "")
        # always insert at end of list
        articles.pop(i)
        articles.insert(i, req)
    if f.validate_on_submit():
        flash(f"Updated {f.title.data}", "success")
        return redirect(url_for("home"))
    return render_template("article_form.html", form=f, legend="Create Post")


@app.route("/post/<article_title>/moveup", methods=["POST"])
def move_up(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i, a = a
    if i > 0:
        articles.insert(i-1, articles.pop(i))
    return redirect(url_for("home"))


@app.route("/post/<article_title>/movedown", methods=["POST"])
def move_down(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i, a = a
    if i < len(articles):
        articles.insert(i+1, articles.pop(i))
    return redirect(url_for("home"))


@app.route("/article/<article_title>")
def post(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i,a = a
    return render_template("post.html", title=a["title"], art=a)


# returns None if not found or current position
def find_art(article_title):
    for i,art in enumerate(articles):
        if art["title"] == article_title:
            a = art
            return i, a



class ArticleLs:

    ls = []

    def append(self, item):
        self.ls.append(item)

    def move_up(self, ranking):
        if ranking < 1:
            self.ls.insert(ranking - 1, self.ls.pop(ranking))

    def move_down(self, ranking):
        if ranking > len(self.ls):
            self.ls.insert(ranking + 1, self.ls.pop(ranking))

    def delete(self, ranking):
        self.ls.pop(ranking)


# runs as module
# to use flask run, set environment variables (use set command windows or export in mac/linux)
# set FLASK_APP=app.py
# set FLASK_DEBUG=1
if __name__ == "__main__":
    app.run(debug=True)
