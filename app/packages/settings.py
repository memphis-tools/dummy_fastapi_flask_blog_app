""" various settings options to be used during application execution """

import os
from dotenv import load_dotenv


DOTENV_NAME = ".envrc.local"
DOTENV_PATH = load_dotenv(DOTENV_NAME)
DEFAULT_ADMIN_NAME = os.getenv("ADMIN_LOGIN")
TEST_USER_USERNAME = "Schtroumpfette"
TEST_USER_PWD = os.getenv("TEST_USER_PWD")

BOOKS_CATEGORIES = [
    "politique",
    "histoire",
    "roman",
    "art",
    "strategie",
    "polar",
    "psychologie",
    "management",
]

TEST_GRAFANA_STATS_PAGE = os.getenv("GRAFANA_URL_ENV_TEST")
PRODUCTION_GRAFANA_STATS_PAGE = os.getenv("GRAFANA_URL_ENV_PROD")
