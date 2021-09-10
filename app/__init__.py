from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
# import exportword
from datetime import date
import os

TODAY = date.today()

# import rank

if os.name != "sdff":
    print(1)

# deal with Pythonanywhere working directory settings...
if os.name == "posix":
    os.chdir("/home/tlebryk1/cybernews")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# crawl_runner = CrawlerRunner(settings=get_project_settings())
# scrape_in_progress = False
# scrape_complete = False

app.config["SECRET_KEY"] = os.environ.get("FLASKKEY", "146abd9")
# make more secure later
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://tlebryk1:flasktake@tlebryk1.mysql.pythonanywhere-services.com/tlebryk1$default"

db = SQLAlchemy(app)
# db.create_all()


# import rank

# deal with Pythonanywhere working directory settings...
if os.name == "posix":
    os.chdir("/home/tlebryk1/cybernews")


# global for now which allows us to keep track of urls that
# our scrapper can't autopopulate
url_ls = []

# see sample_arts.txt  to prepopulate articles for testing purposes
articles = []

from app import routes