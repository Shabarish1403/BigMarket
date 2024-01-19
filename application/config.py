import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    CELERY_BROKER_URL = "redis://127.0.0.1:6969/1"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6969/2"
    REDIS_URL = "redis://127.0.0.1:6969"
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = "127.0.0.1"
    CACHE_REDIS_PORT = 6789
    CACHE_REDIS_DB = 9

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "pf9Wkove4IKEAXvy"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "146585145368132386" # Read from ENV in your case
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "data.sqlite3")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SECURITY_EMAIL_VALIDATOR_ARGS = {"check_deliverability": False}
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    USER_EMAIL_SENDER_EMAIL = 'shabarish.14b@gmail.com'
    CELERY_BROKER_URL = "redis://127.0.0.1:6969/1"
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6969/2"
    REDIS_URL = "redis://127.0.0.1:6969"
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = "127.0.0.1"
    CACHE_REDIS_PORT = 6789
    CACHE_REDIS_DB = 9