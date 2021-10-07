import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    Debug = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "defalt_key")
    CSRF_ENABLED = True
    DATABASE_URL = os.getenv("DATABASE_URL", "error")
    POSTGRESPWD = os.getenv("POSTGRESPWD", "")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL.format(POSTGRESPWD=POSTGRESPWD)
    # SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://postgres:{POSTGRESPWD}@localhost/arts"
    # print(f"POSTGRESPWD: {POSTGRESPWD}")
    # print(f"DATABASE_URL: {DATABASE_URL}")
    # print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True
    # DEVELOPMENT = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    # DEBUG = True
