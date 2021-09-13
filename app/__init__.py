from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import date
from flask_migrate import Migrate
import os
# import rank

TODAY = date.today()

# deal with Pythonanywhere working directory settings...
if os.name == "posix":
    os.chdir("/home/tlebryk1/cybernews")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Crawling globals currenly not functional
# crawl_runner = CrawlerRunner(settings=get_project_settings())
# scrape_in_progress = False
# scrape_complete = False

app.config["SECRET_KEY"] = os.environ.get("FLASKKEY", "146abd9")
sqlpwd = os.environ.get("SQLPWD")

# make more secure later
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://tlebryk1:flasktake@tlebryk1.mysql.pythonanywhere-services.com/tlebryk1$default"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db.create_all()


# deal with Pythonanywhere working directory settings...
if os.name == "posix":
    os.chdir("/home/tlebryk1/cybernews")


# global for now which allows us to keep track of urls that
# our scrapper can't autopopulate
url_ls = []

# see sample_arts.txt  to prepopulate articles for testing purposes
articles = []

from app import routes