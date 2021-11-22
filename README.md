# Daily News Clipping Application

A flask web app to automate compilation of cybersecurity related news. You can currently manually enter fields, autopopulate the fields by simply entering a url, or use machine learning on the "daily-scrape" tab to automatically collect and return the top 8 cybersecurity articles from the last day. The app exports the days stories in proper FDD format. See the guide on your intern drive emailed to you during onboarding for more information.

## Setting up a development enviornment

This project will be moved back to docker soon, but for now you will need the following to working on this app locally.

1. Install all the packages from the `requirements.txt` in a python environment.
2. Download [Postgres](https://www.postgresql.org/download/) and follow any installation instructions there. You can optionally set up a password which you'll need to remember.
3. Set up a database named 'arts'. You can follow the instructions from [this tutorial](https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/). Briefly, using the default settings, you will likely need to run:

```
psql -U postgres
create database arts;
```

Quit the postgres shell (control+c) or open up a new terminal. Initiate the database by running:

```
cd app
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

The app module should generally handle migrations for you after initialization. If you re-enter the postgres shell, you should be able to run `\c arts` and then `\dt` to view the existing relations.

4. Create a `.env` file with the following information:

```
DATABASE_URL=postgresql+psycopg2://postgres:{POSTGRESPWD}@localhost/arts
POSTGRESPWD=somepasswordyouset
SECRET_KEY=somerandomkeyyouset
FLASK_ENV=development
```

## Deployment

The app is currently deployed on Heroku. The production version is available at https://flask-exmpl-app.herokuapp.com/ (sorry for the corny url). The `heroku-staging` branch is matched with a heroku remote repository. Pushes to the `heroku-staging` branch will automatically initiate a build on heroku. The resulting dev server is available at https://flask-app-staging.herokuapp.com/. Promoting the staging environment to production can be done via heroku command line or via the heroku dashboard.

## Directory navigation:

- [`scrapers/`](scrapers/): contains the spiders and settings for automated collection of the days news articles. The home directory is already set up as a scrapy project, so you do not need to enter the scrapers directory to run use the scrapy CLI during development.

- [`migrations\`](migrations\): migrations for the postgres database.

- [`app`](app/): flask app module. Run with `run.py`. Currently needs more in file documentation. Todo: create loading page during dailyscrape. 

- Other relevant files:
  - `Procfile`: holds the command to run the app on heroku
  - `runtime.txt`: determines the python version to use on heroku. You should also develop in that version locally.
  - `scrapy.cfg`: configures the scrapy project.
  - `config.py`: config settings for the app
