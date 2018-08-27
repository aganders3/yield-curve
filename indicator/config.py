import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    basedir = os.environ.get('DB_BASE_DIR') or BASE_DIR
    SQLALCHEMY_DATABASE_URI =  default_db_path or \
        'sqlite:///' + os.path.join(basedir, 'indicator.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
