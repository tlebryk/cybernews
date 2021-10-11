import logging
import os
from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_migrate import Migrate
from forms import ArticleForm, AutoPopForm
from flask_sqlalchemy import SQLAlchemy
import exportword
from zotero import get_meta

HOMEDIR = os.path.expanduser("~")
DATETIMENOW = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    # datefmt="%Y-%m-%d %H:%M:%S",
    # filename=f"{HOMEDIR}/Desktop/repos/protocol-china/wipo/logs/run_wipopagelink_scraper/scrapy_wipo_{DATETIMENOW}.log",
    level=logging.INFO,
)
logging.basicConfig(level=logging.INFO)

TODAY = date.today()
app = Flask(__name__)
# fetch Config class, as set by APP_SETTINGS environment var, 
# but defaulting to DevelopmentConfig in config.py
# APP_SETTIGNS should be one of : config.DevelopmentConfig/ProductionConfig/Config/StagingConfig/DevelopmentConfig
# you can set this for heroku app using: 
# heroku config:set --remote staging SECRET_KEY=the-staging-key APP_SETTINGS=config.StagingConfig
# NOTE: for prod run: 
# heroku config:set --remote prod SECRET_KEY=prodkey APP_SETTINGS=config.ProductionConfig
# to display heroku vars: 
#  heroku config --remote staging
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# update app with config variables
# to fetch config variables run something like: app.config.get("SECRET_KEY")
app.config["SECRET_KEY"] = "6f1f6f1c724600453622f48c48555e73"
migrate = Migrate(app, db)
from models import Articles

articles = []

# @app.route("/")
# @app.route("/home", methods=["GET", "POST"])
# def home():
#     logging.info(articles)
#     return render_template("home.html", articles=articles)

# @app.route("/article_form", methods=["POST", "GET"])
# def add_article():
#     f = ArticleForm()
#     if request.method == "POST":
#         req = request.form.copy()
#         req["body"] = req["body"].replace("\r", "")
#         articles.append(req)
#     if f.validate_on_submit():
#         flash(f"Added {f.title.data}", "success")
#         return redirect(url_for("home"))
#     return render_template("article_form.html", form=f, legend="Create Post")

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
    # logging.info(f"head: {head}")
    # logging.info([(k, v) for k, v in elementdict.items()])
    newlist = []
    while head:
        logging.info(f"head id: {head.id}, prev: {head.prevart}, next: {head.nextart}")
        newlist.append(head)
        ind = elementdict.get(head.prevart)
        # ind can == 0 so specify None
        if ind == None:
            logging.info(f"get {head.prevart} came up empty breaking")
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
    nxtnxt = Articles.query.get(nxt.nextart)

    # logging.info(f"original a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    # logging.info(f"move_up prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    # logging.info(f"move_up nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    if prev and nxt:
        nxt.prevart = prev.id
        prev.nextart = nxt.id
        a.nextart = nxt.nextart
        a.prevart = nxt.id
        nxt.nextart = a.id
        logging.info("prev and nxt hit")
    elif nxt:
        nxt.prevart = 0
        a.nextart = nxt.nextart
        a.prevart = nxt.id
        nxt.nextart = a.id
        logging.info("nxt only hit")
    if nxtnxt:
        nxtnxt.prevart = a.id

    # logging.info(f"move up after a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    # logging.info(f"move_up after: prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    # logging.info(f"move_up after nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
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
    prevprev = Articles.query.get(prev.prevart)

    # logging.info(f"original a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    # logging.info(f"move_down prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    # logging.info(f"move_down nxt: {nxt.id}, prev: {nxt.prevart}, next: {nxt.nextart}")
    if prev and nxt:
        nxt.prevart = prev.id
        prev.nextart = nxt.id
        a.nextart = prev.id
        a.prevart = prev.prevart
        prev.prevart = a.id
        logging.info("prev and nxt hit")
    elif prev:
        prev.nextart = 0
        a.nextart = prev.id
        a.prevart = prev.prevart
        prev.prevart = a.id
        logging.info("prev only hit")
    if prevprev:
        prevprev.nxt = a.id
    # logging.info(f"move down after a: id: {a.id}, prev: {a.prevart}, next: {a.nextart}")
    # logging.info(f"move_down after: prev: {prev.id}, prev: {prev.prevart}, next: {prev.nextart}")
    # logging.info(f"move_down after nxt: {nxt.id}, nxt: {nxt.prevart}, next: {nxt.nextart}")
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/article/<int:art_id>")
def post(art_id=None):
    a = Articles.query.get_or_404(art_id)
    return render_template("post.html", title=a.title, art=a)
    
@app.route("/export", methods=["POST"])
def background_export():
    """ Downloads articles as word document in proper formatting"""
    if not os.path.exists("docs"):
        os.makedirs("docs")
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
    # logging.info(f"head: {head}")
    # logging.info([(k, v) for k, v in elementdict.items()])
    articles = []
    while head:
        logging.info(f"head id: {head.id}, prev: {head.prevart}, next: {head.nextart}")
        articles.append(head)
        ind = elementdict.get(head.prevart)
        # ind can == 0 so specify None
        if ind == None:
            logging.info(f"get {head.prevart} came up empty breaking")
            break
        head = unsortarts[ind]
    if request.method == "POST":
        exportword.cyber_export(
            f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx", articles
        )
        path = f"docs/Cyber_Briefing_{TODAY.strftime('%B_%d_%Y')}.docx"
        return send_file(path, as_attachment=True)
    return render_template("home.html", articles=articles)


@app.route("/crawl2", methods=["POST"])
def crawl2(url_ls):
    """Send urls to a zotero translationserver and
        return the index of the first such article and
        number of articles added [under construction]
    """
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
    if not url_ls:
        return False
    # nxtart = None
    for i, url in enumerate(url_ls):
        data = get_meta(url)
        article = Articles(
            url = data["url"],
            title=data["title"],
            authors=data["author"],
            body=data["body"],
            source=data["source"],
            artdate=data["date"],
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
        logging.info(f"added article: {data}")
        # save id of first entry
        if i == 0:
            start = article.id
        nextart = article
    return start



@app.route("/url_form", methods=["POST", "GET"])
def url_form():
    """Currently not fuctional
    Allows user to add urls for select sites, will autopopulate information
    """
    f = AutoPopForm()
    if request.method == "POST":
        req = request.form.copy()
        req.pop("submit")
        req.pop("csrf_token")
        url_ls = [v for v in req.values() if v]
        # url_clump = AS.sort_urls2(url_ls)
        result = crawl2(url_ls=url_ls)
        if not result:
            flash(f"No urls", "warning")
            return redirect(url_for("home"))
    if f.validate_on_submit():
        flash(f"Added urls", "success")
        return redirect(url_for("update_post",
            art_id=result))
    return render_template("url_form.html", form=f, legend="Create Post")

# @app.route("/post/<article_title>/delete_post", methods=["POST"])
# def delete_post(article_title):
#     a = find_art(article_title)
#     if not a:
#         flash(f"Article not found")
#     i, _ = a
#     articles.pop(i)
#     return redirect(url_for("home"))

# @app.route("/delete_all", methods=["POST"])
# def delete_all():
#     global articles
#     articles = []
#     return redirect(url_for("home"))

# # returns None if not found or current position
# def find_art(article_title):
#     for i, art in enumerate(articles):
#         if art["title"] == article_title:
#             a = art
#             return i, a

# # downloads articles as word document in proper formatting
# @app.route("/export", methods=["POST"])
# def background_export():
#     pass
#     # if request.method == "POST":
#     #     exportword.cyber_export(
#     #         f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx", articles
#     #     )
#     #     path = f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx"
#     #     return send_file(path, as_attachment=True)
#     # return render_template("home.html", articles=articles)


# @app.route("/post/<article_title>/moveup", methods=["POST"])
# def move_up(article_title):
#     a = find_art(article_title)
#     if not a:
#         flash(f"Article not found")
#         return redirect(url_for("home"))
#     i, a = a
#     if i > 0:
#         articles.insert(i - 1, articles.pop(i))
#     return redirect(url_for("home"))


# @app.route("/post/<article_title>/movedown", methods=["POST"])
# def move_down(article_title):
#     a = find_art(article_title)
#     if not a:
#         flash(f"Article not found")
#         return redirect(url_for("home"))
#     i, a = a
#     if i < len(articles):
#         articles.insert(i + 1, articles.pop(i))
#     return redirect(url_for("home"))


# @app.route("/article/<article_title>")
# def post(article_title):
#     a = find_art(article_title)
#     if not a:
#         flash("Article not found", "warning")
#         return redirect(url_for("home"))
#     _, a = a
#     return render_template("post.html", title=a["title"], art=a)


    """
set DATABASE_URL=postgres://$(whoami)
set FLASK_DEBUG=1
set FLASK_ENV=development & flask run
to move from staging to prod:
heroku pipelines:promote -- remote staging
"""