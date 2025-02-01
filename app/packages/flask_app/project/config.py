""" The common config file used by the Flask app """

import os
import datetime

try:
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages.utils import get_secret

basedir = os.path.abspath(os.path.dirname(__file__))


if os.getenv("SCOPE") == "production":
    db_name = os.getenv("POSTGRES_PRODUCTION_DB_NAME")
else:
    db_name = os.getenv("POSTGRES_TEST_DB_NAME")

username = os.getenv("POSTGRES_USER")
if os.getenv("SCOPE") == "production" or os.getenv("SCOPE") == "development":
    password = get_secret("/run/secrets/POSTGRES_PASSWORD")
    ADMIN_EMAIL = get_secret("/run/secrets/ADMIN_EMAIL")
    CELERY_BROKER_URL = get_secret("/run/secrets/CELERY_BROKER_URL")
    HCAPTCHA_SITE_SECRET = get_secret("/run/secrets/HCAPTCHA_SITE_SECRET")
    SECRET_KEY = get_secret("/run/secrets/SECRET_KEY")
    SENDGRID_API_KEY = get_secret("/run/secrets/SENDGRID_API_KEY")
else:
    password = os.getenv("POSTGRES_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    HCAPTCHA_SITE_SECRET = os.getenv("HCAPTCHA_SITE_SECRET")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database_name = db_name
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database_name}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

HCAPTCHA_VERIFY_URL = "https://api.hcaptcha.com/siteverify"
HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY")
HCAPTCHA_ENABLED = True

MAX_CONTENT_LENGTH = 1024 * 1024 * 5

REMEMBER_COOKIE_DURATION = datetime.timedelta(days=1)
