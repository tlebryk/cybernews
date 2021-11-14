import logging
import os
from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# update app with config variables
# to fetch config variables run something like: app.config.get("SECRET_KEY")
app.config["SECRET_KEY"] = "6f1f6f1c724600453622f48c48555e73"
migrate = Migrate(app, db)

from app import routes
