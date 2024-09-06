""" The common config file used by the Flask app """

import os
import datetime


basedir = os.path.abspath(os.path.dirname(__file__))

scope = os.getenv("SCOPE")
if scope == "test" or scope is None:
    db_name = os.getenv("POSTGRES_TEST_DB_NAME")
elif scope == "production":
    db_name = os.getenv("POSTGRES_PRODUCTION_DB_NAME")
else:
    db_name = os.getenv("POSTGRES_TEST_DB_NAME")
username = os.getenv("ADMIN_LOGIN")
password = os.getenv("ADMIN_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database_name = db_name

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database_name}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=1)

HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"
HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY")
HCAPTCHA_SITE_SECRET = os.getenv("HCAPTCHA_SITE_SECRET")
HCAPTCHA_ENABLED = True

CELERY_BROKER_URL = "pyamqp://dummy_ops_admin:@pplepie94@rabbitmq:5672/dummy_ops_admin_vhost"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

MAX_CONTENT_LENGTH = 1024 * 1024 * 5

EMAIL_SERVER = os.getenv("EMAIL_SERVER")
LOCAL_EMAIL_LOGS_FILE = os.getenv("LOCAL_EMAIL_LOGS_FILE")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
