import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    DB_HOST = 't'
    DB_USER = ''
    DB_PASSWORD = ''
    DB_NAME = ''
    

    @staticmethod
    def get_database_uri():
        return f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}" #?reconnect=true"
