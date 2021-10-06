from flask import Flask, render_template, redirect, url_for, request, flash 
from forms import ArticleForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "6f1f6f1c724600453622f48c48555e73"

articles = []

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html", articles=articles)

"""
set FLASK_ENV=development & set FLASK_DEBUG=1 & flask run
"""

@app.route("/article_form", methods=["POST", "GET"])
def add_article():
    f = ArticleForm()
    if request.method == "POST":
        req = request.form.copy()
        req["body"] = req["body"].replace("\r", "")
        articles.append(req)
    if f.validate_on_submit():
        flash(f"Added {f.title.data}", "success")
        return redirect(url_for("home"))
    return render_template("article_form.html", form=f, legend="Create Post")

@app.route("/post/<article_title>/delete_post", methods=["POST"])
def delete_post(article_title):
    a = find_art(article_title)
    if not a:
        flash(f"Article not found")
    i, _ = a
    articles.pop(i)
    return redirect(url_for("home"))

@app.route("/delete_all", methods=["POST"])
def delete_all():
    global articles
    articles = []
    return redirect(url_for("home"))

# returns None if not found or current position
def find_art(article_title):
    for i, art in enumerate(articles):
        if art["title"] == article_title:
            a = art
            return i, a

# downloads articles as word document in proper formatting
@app.route("/export", methods=["POST"])
def background_export():
    pass
    # if request.method == "POST":
    #     exportword.cyber_export(
    #         f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx", articles
    #     )
    #     path = f"docs/Cyber_Briefing_{td.strftime('%B_%d_%Y')}.docx"
    #     return send_file(path, as_attachment=True)
    # return render_template("home.html", articles=articles)


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


@app.route("/article/<article_title>")
def post(article_title):
    a = find_art(article_title)
    if not a:
        flash("Article not found", "warning")
        return redirect(url_for("home"))
    _, a = a
    return render_template("post.html", title=a["title"], art=a)