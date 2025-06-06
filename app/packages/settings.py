""" various settings options to be used during application execution """

import os

INSTANCE_PATH = "/home/dummy-operator/flask/"

DEFAULT_ADMIN_NAME = os.getenv("ADMIN_LOGIN")
TEST_USER_USERNAME = "Schtroumpfette"
TEST_USER_PWD = os.getenv("TEST_USER_PWD")
DEFAULT_NEW_PASSWORD_MIN_LENGTH = 10
DEFAULT_NEW_PASSWORD_MAX_LENGTH = 75
DEFAULT_NEW_PASSWORD_MIN_DIGITS = 1
DEFAULT_NEW_PASSWORD_MIN_SPECIAL_CHAR = 1
ALLOWED_SPECIALCHARS_IN_PASSWORD = ["@", "?", "!", "%", "$", "^", "+"]
FORBIDDEN_SPECIALCHARS_IN_PASSWORD = [
    " ",
    ",",
    "`",
    "|",
    "/",
    "\\",
    "{",
    "}",
    "[",
    "]",
    "*",
    ":",
    ";",
    "<",
    ">"
]

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

PIE_COLORS = [
    "orange",
    "cyan",
    "green",
    "yellow",
    "pink",
    "brown",
    "beige",
    "grey",
    "yellowgreen",
    "gold",
    "lightcoral",
    "lightskyblue",
]

POSTS_PER_PAGE = 6
UPLOAD_EXTENSIONS = [".jpg", ".jpeg", ".png"]
