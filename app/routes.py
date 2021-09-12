from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from app import db, TODAY
from app.forms import ArticleForm, AutoPopForm
from app.models import Articles
from app import app, articles, url_ls
import logging
from sqlalchemy import desc, text
@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    articles = Articles.query.filter_by(briefingdate=TODAY).all()
    return render_template("home.html", articles=articles)


@app.route("/article_form", methods=["POST", "GET"])
def add_article():
    f = ArticleForm()
    # if request.method == "POST":
    #     req = request.form.copy()
    #     req["body"] = req["body"].replace("\r", "")
    #     articles.append(req)
    if f.validate_on_submit():
        arts = Articles.query.filter_by(briefingdate=TODAY)
        # regardless of which element is returned first,
        # backwards traversal will always land on the final element
        # final = arts.order_by(desc(text('articles.ranking'))).first()
        final = arts.first()
        if not final:
            class filler():
                id=0
                prevart=None
            final = filler()
            logging.info("No articles found during add_article. Initializing today's linked list")
        else:
            counter = 0
            while final.prevart and counter < 1000:
                final = Articles.query.get(final.prevart)
                counter+=1
            logging.info(f"""finalprevart:{final.prevart};
                finalnextart:{final.nextart};
                finalid: {final.id};
                finaltitle: {final.title};""")

        # final.prevart =
        # for article in articles:
        #     article.prev
        # gimmicky ranking system
        # with 20 element operation max
        ranking = 20 * (arts.count() + 1)
        # traverse list until last element fond
        # Articles.query.filter_by(briefingdate=TODAY).last()
        article = Articles(
            url = f.url.data,
            title = f.title.data,
            authors = f.author.data,
            body = f.body.data,
            source = f.source.data,
            artdate = f.date.data,
            prevart = 0,
            nextart = final.id,
            ranking = ranking,
        )
        db.session.add(article)
        db.session.flush()
        db.session.refresh(article)
        logging.info(f"prev art before: {final.prevart}")
        final.prevart = article.id
        logging.info(f"prev art after: {final.prevart}")
        db.session.commit()
        flash(f"Added {f.title.data}; finalprevart:{final.prevart}; finalid: {final.id}; newntext{article.nextart}; newid: {article.id}; lastid: {article.prevart}", "success")

        logging.info(f"added article: {f}")

    if f.homesub.data:
        return redirect(url_for("home"))
    elif f.nextsub.data:
            # if len(articles) <= i+1:
                # flash(f"Updated {f.title.data} TESTING", "success")
        return redirect(url_for("add_article"))
            # else:
                # return redirect(url_for("update_post",
                    # article_title=articles[i+1]['title']))
        # return redirect(url_for("home"))
    return render_template("article_form.html", form=f, legend="Create Post")


# Allows user to add urls
# for select sites, will autopopulate information
@app.route("/url_form", methods=["POST", "GET"])
def url_form():
    f = AutoPopForm()
    if request.method == "POST":
        req = request.form.copy()
        req.pop("submit")
        req.pop("csrf_token")
        global url_ls
        url_ls = [v for v in req.values() if v]
        # url_clump = AS.sort_urls2(url_ls)
        result = crawl2(url_ls=url_ls)
        if not result:
            flash(f"No urls", "warning")
            return redirect(url_for("home"))
    if f.validate_on_submit():
        start, _ = result
        flash(f"Added urls", "success")
        return redirect(url_for("update_post",
            article_title=articles[start]['title']))
    return render_template("url_form.html", form=f, legend="Create Post")


@app.route("/post/<int:art_id>/delete_post", methods=["POST"])
def delete_post(art_id):
    a = Articles.query.get_or_404(art_id)
    if not a:
        flash(f"Article not found")
    db.session.delete(a)
    db.session.commit()
    flash(f"{a.title} has been deleted", "success")

    # a = find_art(article_title)

    # i, _ = a
    # articles.pop(i)
    return redirect(url_for("home"))

@app.route("/delete_all", methods=["POST"])
def delete_all():
    articles = Articles.query.filter_by(briefingdate=TODAY)
    articles.delete()
    # db.session.delete(articles)
    db.session.commit()
    # as = Article.query.get
    # global articles
    # articles = []
    return redirect(url_for("home"))


@app.route("/post/<int:art_id>/update", methods=["POST", "GET"])
def update_post(art_id):
    a = Articles.query.get_or_404(art_id)
    # a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    # i, a = a
    f = ArticleForm()
    if request.method == "GET":
        f.title.data = a.title
        f.body.data = a.body
        f.url.data = a.url
        f.source.data = a.source
        f.author.data = a.authors
        f.date.data = a.artdate
    # if request.method == "POST":
    #     req = request.form.copy()
    #     req["body"] = req["body"].replace("\r", "")
    #     articles.pop(i)
    #     articles.insert(i, req)
    if f.validate_on_submit():
        a.title = f.title.data
        a.body = f.body.data
        a.url = f.url.data
        a.source = f.source.data
        a.authors = f.author.data
        a.artdate = f.date.data
        db.session.commit()
        flash(f"Updated {f.title.data}", "success")
        if f.homesub.data:
            return redirect(url_for("home"))
        # if f.nextsub.data:
            # if len(articles) <= i+1:
                # flash(f"Updated {f.title.data} TESTING", "success")
                # return redirect(url_for("add_article"))
            # else:
                # return redirect(url_for("update_post",
                    # article_title=articles[i+1]['title']))
    return render_template("article_form.html", form=f, legend="Update Post")


@app.route("/post/<article_title>/moveup", methods=["POST"])
def move_up(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i, a = a
    if i > 0:
        articles.insert(i - 1, articles.pop(i))
    return redirect(url_for("home"))


@app.route("/post/<article_title>/movedown", methods=["POST"])
def move_down(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    i, a = a
    if i < len(articles):
        articles.insert(i + 1, articles.pop(i))
    return redirect(url_for("home"))


@app.route("/article/<int:art_id>")
def post(art_id=None):
    a = Articles.query.get_or_404(art_id)
    # a = find_art(article_title)
    # if not a:
    #     flash("Article not found", "warning")
    #     return redirect(url_for("home"))
    # _, a = a
    return render_template("post.html", title=a.title, art=a)


# @app.route("/crawl")
# def crawl(url_clump):
#     global scrape_in_progress
#     global scrape_complete

#     if not scrape_in_progress:
#         scrape_in_progress = True
#         global articles
#         # start the crawler and execute a callback when complete
#         for clump in url_clump.values():
#             r = crawl_runner.crawl(
#                 clump.Spider,
#                 **dict(start_urls=clump._url_ls, date_check=False, articles=articles),
#             )
#         r.addCallback(finished_scrape)

# @app.route("/crawl2", methods=['POST'])
# def crawl2(url_ls):
#     global articles
#     start = len(articles)
#     if not url_ls:
#         return False
#     for url in url_ls:
#         articles.append(get_meta(url))
#     return start, len(url_ls)





# @app.route("/dailyscrape")
# def getdaily():
#     try:
#         df = DR.get_todays_js()
#     except ValueError:
#         flash(f"No articles found", "warning")
#         return redirect(url_for("home"))
#     df = rank.sort(df)
#     # df.date = df.date.dt.strftime("%B %d, %Y")
#     arts = df.to_json(orient="records")
#     df.date = str(df.date)
#     a = json.loads(arts)
#     # arts = DR.main(process=crawl_runner)
#     a = a[::-1]
#     for el in a:
#         for key, value in el.items():
#             el[key] = str(value)
#     # [print(type(x), x) for x in a[1].values()]
#     articles.extend(a[:7])
#     return redirect(url_for("home"))


# For testing purposes:
# Get the results only if a spider has results
@app.route("/results")
def get_results():
    global scrape_complete
    if scrape_complete:
        return articles
    return "Scrape Still Progress"


# downloads articles as word document in proper formatting
@app.route("/export", methods=["POST"])
def background_export():

    if request.method == "POST":
        exportword.cyber_export(
            f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx", articles
        )
        path = f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx"
        return send_file(path, as_attachment=True)
    return render_template("home.html", articles=articles)


# for testing purposes
@app.route("/printer", methods=["GET", "POST"])
def printer():
    for a in articles:
        print(a)
    return render_template("home.html", articles=articles)


# returns None if not found or current position
def find_art(article_title):
    for i, art in enumerate(articles):
        if art["title"] == article_title:
            a = art
            return i, a


def url_lookup(url_ls):
    settings = get_project_settings()
    settings["FEEDS"] = {
        "test1.json": {"format": "json", "encoding": "utf8", "overwrite": False}
    }
    process = AS.get_articles(url_ls, settings)
    process.start()
    articles.extend(AS.DICT_LS)


# A callback that is fired after the scrape has completed.
# Set a flag to allow display the results from /results
def finished_scrape(null):
    global scrape_complete
    scrape_complete = True


# Eventual class to include attributes on articles
# For now, articles are stored in a list
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
