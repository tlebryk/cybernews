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
    unsortarts = Articles.query.filter_by(briefingdate=TODAY).all()
    # store id as key, unsorted index as value
    elementdict = {}
    head = 0
    for i, a in enumerate(unsortarts):
        elementdict[a.id] = i
        if a.nextart == 0:
            head = a
        # if a.prevart == 0:
        #     tail = a
    # logging.info(f"tail: {tail}")
    logging.info(f"head: {head}")
    logging.info([(k, v) for k, v in elementdict.items()])
    newlist = []
    while head:
        newlist.append(head)
        ind = elementdict.get(head.prevart)
        if not ind:
            break
        head = unsortarts[ind]
    return render_template("home.html", articles=newlist)


@app.route("/article_form", methods=["POST", "GET"])
def add_article():
    f = ArticleForm()
    if f.validate_on_submit():
        arts = Articles.query.filter_by(briefingdate=TODAY)
        # regardless of which element is returned first,
        # backwards traversal will always land on the final element
        final = arts.first()
        if not final:

            class filler:
                id = 0
                prevart = None

            final = filler()
            logging.info(
                "No articles found during add_article. Initializing today's linked list"
            )
        else:
            counter = 0
            while final.prevart and counter < 1000:
                final = Articles.query.get(final.prevart)
                counter += 1
            logging.info(
                f"""finalprevart:{final.prevart};
                finalnextart:{final.nextart};
                finalid: {final.id};
                finaltitle: {final.title};"""
            )
        # # gimmicky ranking system
        # # with 20 element operation max
        # ranking = 20 * (arts.count() + 1)
        article = Articles(
            url=f.url.data,
            title=f.title.data,
            authors=f.author.data,
            body=f.body.data,
            source=f.source.data,
            artdate=f.date.data,
            prevart=0,
            nextart=final.id,
            # ranking = ranking,
        )
        db.session.add(article)
        db.session.flush()
        db.session.refresh(article)
        logging.info(f"final prev art before: {final.prevart}")
        final.prevart = article.id
        logging.info(f"final prev art after: {final.prevart}")
        db.session.commit()
        logging.info(f"added article: {f}")
    if f.homesub.data:
        return redirect(url_for("home"))
    elif f.nextsub.data:
        return redirect(url_for("add_article"))
    return render_template("article_form.html", form=f, legend="Create Post")


@app.route("/post/<int:art_id>/delete_post", methods=["POST"])
def delete_post(art_id):
    a = Articles.query.get_or_404(art_id)
    if not a:
        flash(f"Article not found")
    else:
        prev = Articles.query.get(a.prevart)
        nxt = Articles.query.get(a.nextart)
        if prev and nxt:
            prev.nextart = nxt.id
            nxt.prevart = prev.id
        elif prev:
            prev.nextart = 0
        elif nxt:
            nxt.prevart = 0
    db.session.delete(a)
    db.session.commit()
    flash(f"{a.title} has been deleted", "success")
    return redirect(url_for("home"))


@app.route("/delete_all", methods=["POST"])
def delete_all():
    articles = Articles.query.filter_by(briefingdate=TODAY)
    articles.delete()
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/post/<int:art_id>/update", methods=["POST", "GET"])
def update_post(art_id):
    a = Articles.query.get_or_404(art_id)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    f = ArticleForm()
    if request.method == "GET":
        f.title.data = a.title
        f.body.data = a.body
        f.url.data = a.url
        f.source.data = a.source
        f.author.data = a.authors
        f.date.data = a.artdate
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
    return render_template("article_form.html", form=f, legend="Update Post")


@app.route("/post/<int:art_id>/moveup", methods=["POST"])
def move_up(art_id):
    a = Articles.query.get(art_id)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    prev = Articles.query.get(a.prevart)
    nxt = Articles.query.get(a.nextart)
    logging.info(f"original a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    logging.info(f"move_up prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    logging.info(f"move_up nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    if prev and nxt:
        nxt.prevart = prev.id
        prev.nextart = nxt.id
        a.nextart = nxt.nextart
        a.prevart = nxt.id
        nxt.nextart = a.id
    elif nxt:
        nxt.prevart = 0
        a.nextart = nxt.nextart
        a.prevart = nxt.id
        nxt.nextart = a.id
    logging.info(f"move up after a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    logging.info(f"move_up after: prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    logging.info(f"move_up after nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/post/<int:art_id>/movedown", methods=["POST"])
def move_down(art_id):
    a = Articles.query.get(art_id)
    if not a:
        flash(f"Article not found")
        return redirect(url_for("home"))
    prev = Articles.query.get(a.prevart)
    nxt = Articles.query.get(a.nextart)
    logging.info(f"original a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    logging.info(f"move_up prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    logging.info(f"move_up nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    if prev and nxt:
        nxt.prevart = prev.id
        prev.nextart = nxt.id
        a.nextart = prev.id
        a.prevart = prev.prevart
        prev.prevart = a.id
    elif prev:
        prev.nextart = 0
        a.nextart = prev.id
        a.prevart = prev.prevart
        prev.prevart = a.id
    logging.info(f"move up after a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    logging.info(f"move_up after: prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    logging.info(f"move_up after nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/article/<int:art_id>")
def post(art_id=None):
    a = Articles.query.get_or_404(art_id)
    return render_template("post.html", title=a.title, art=a)


@app.route("/export", methods=["POST"])
def background_export():
    """ Downloads articles as word document in proper formatting"""
    if request.method == "POST":
        exportword.cyber_export(
            f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx", articles
        )
        path = f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx"
        return send_file(path, as_attachment=True)
    return render_template("home.html", articles=articles)


@app.route("/printer", methods=["GET", "POST"])
def printer():
    """ for testing purposes"""
    for a in articles:
        print(a)
        logging.info(a)
    return render_template("home.html", articles=articles)


@app.route("/url_form", methods=["POST", "GET"])
def url_form():
    """Currently not fuctional
    Allows user to add urls for select sites, will autopopulate information
    """
    pass
    # f = AutoPopForm()
    # if request.method == "POST":
    #     req = request.form.copy()
    #     req.pop("submit")
    #     req.pop("csrf_token")
    #     global url_ls
    #     url_ls = [v for v in req.values() if v]
    #     # url_clump = AS.sort_urls2(url_ls)
    #     result = crawl2(url_ls=url_ls)
    #     if not result:
    #         flash(f"No urls", "warning")
    #         return redirect(url_for("home"))
    # if f.validate_on_submit():
    #     start, _ = result
    #     flash(f"Added urls", "success")
    #     return redirect(url_for("update_post",
    #         article_title=articles[start]['title']))
    # return render_template("url_form.html", form=f, legend="Create Post")


# @app.route("/results")
# def get_results():
#     """Not Functional; For testing purposes"""
#     global scrape_complete
#     if scrape_complete:
#         return articles
#     return "Scrape Still Progress"


# @app.route("/crawl")
# def crawl(url_clump):
#  """Not functional """
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
#     """Not functional """
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

# def finished_scrape(null):
#     """ Not Functional
#      A callback that is fired after the scrape has completed.
#     Set a flag to allow display the results from /results"""
#     global scrape_complete
#     scrape_complete = True


# class ArticleLs:
#     """ Deprecated"""

#     ls = []

#     def append(self, item):
#         self.ls.append(item)

#     def move_up(self, ranking):
#         if ranking < 1:
#             self.ls.insert(ranking - 1, self.ls.pop(ranking))

#     def move_down(self, ranking):
#         if ranking > len(self.ls):
#             self.ls.insert(ranking + 1, self.ls.pop(ranking))

#     def delete(self, ranking):
#         self.ls.pop(ranking)


# def url_lookup(url_ls):
#     """Deprecated"""
#     settings = get_project_settings()
#     settings["FEEDS"] = {
#         "test1.json": {"format": "json", "encoding": "utf8", "overwrite": False}
#     }
#     process = AS.get_articles(url_ls, settings)
#     process.start()
#     articles.extend(AS.DICT_LS)


# def find_art(article_title):
#     """Deprecated
#       returns None if not found or current position"""
#     for i, art in enumerate(articles):
#         if art["title"] == article_title:
#             a = art
#             return i, a
