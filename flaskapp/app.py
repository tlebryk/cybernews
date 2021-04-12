from flask import Flask, render_template, url_for, flash, redirect, request
from forms import ArticleForm
import exportword

app = Flask(__name__)

# filler; make environment variable later
app.config["SECRET_KEY"] = "6f1f6f1c724600453622f48c48555e73"

# for testing purposes, prepopulate 2 articles
articles = [
    {'title': "filler",
    "author": "Sara Friedman",
    "body": "basfd \n adsfa \n dasfas \n adsfas \n",
    "url": "https://insidecybersecurity.com/daily-news/lawmakers-federal-officials-begin-examining-next-set-cyber-policy-needs-amid-covid-and",
    "source": "Inside Cybersecurity",
    "date": "March 2, 2021",},
    
    {'title': "filler2",
    "author": "Tonya Riley",
    "body": "asdfsfasf \n asfasdfdsf \n asfddds \n adsasfdasdfafas \n",
    "url": "https://www.cyberscoop.com/us-intelligence-report-warns-of-increased-offensive-cyber-disinformation-around-the-world/",
    "source": "CyberScoop",
    "date": "March 1, 2021",},
    

]


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        exportword.cyber_export("test.docx", articles)
    return render_template("home.html", articles=articles)


@app.route('/export', methods=["POST"])
def background_export():
    exportword.cyber_export("test1.docx", articles)
    return render_template("home.html", articles=articles)


@app.route("/article_form", methods=["GET", "POST"])
def add_article():
    f = ArticleForm()
    if request.method == "POST":
        req = request.form
        articles.append(req)
    if f.validate_on_submit():
        flash(f"Added {f.title.data}", 'success')
        return redirect(url_for("home"))
    return render_template("article_form.html", form=f)

@app.route("/scraper")
def scraper():
    return "<h1>Scraper<h1>"

@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "/test1.docx"
    return send_file(path, as_attachment=True)

# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#    if request.method == 'POST':
#       result = request.form
#     return render_template("display.html",result = result)

# runs as module
# to use flask run, set environment variables (use set command windows or export in mac/linux)
# set FLASK_APP=app.py
# set FLASK_DEBUG=1
if __name__ == "__main__":
    app.run(debug=True)


