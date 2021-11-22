import logging
import os
from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

CURRENTDIR = os.getcwd()
DATETIMENOW = datetime.now().strftime("%Y%m%d_%H%M%S")
LOGPATH = f"{CURRENTDIR}/logs/{__file__}/"


TODAY = date.today()
app = Flask(__name__)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# update app with config variables
migrate = Migrate(app, db)

# todo: set up production logging
if app.config.get("development"):
    if not os.path.exists(LOGPATH):
        os.makedirs(LOGPATH)
    logging.basicConfig(
        filename=f"{LOGPATH}/{DATETIMENOW}.log",
        format="%(asctime)s %(levelname)-8s  %(filename)s %(lineno)d %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


from app import routes
