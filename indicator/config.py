import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    default_db_path = os.path.join(os.environ.get('DATABASE_BASEDIR'), 'indicator.db')
    SQLALCHEMY_DATABASE_URI =  default_db_path or \
        'sqlite:///' + os.path.join(basedir, 'indicator.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
