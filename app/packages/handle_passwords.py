""" check password againt a policy """

from flask import (
    Flask,
    url_for,
    render_template,
    flash,
    abort,
    redirect,
    request,
    Response,
)
from app.packages import settings


def check_digit(plain_password):
    digit_count = 0
    for char in plain_password:
        if char.isdigit():
            digit_count += 1
    return digit_count


def check_special_chars(plain_password):
    special_chars_count = 0
    forbidden_chars_count = 0
    for char in plain_password:
        if char in settings.ALLOWED_SPECIALCHARS_IN_PASSWORD:
            special_chars_count += 1
        if char in settings.FORBIDDEN_SPECIALCHARS_IN_PASSWORD:
            forbidden_chars_count += 1
    return all(
        [
            special_chars_count >= settings.DEFAULT_NEW_PASSWORD_MIN_SPECIAL_CHAR,
            forbidden_chars_count == 0,
        ]
    )


def check_password(plain_text_password):
    """
    Description: check if password respects the min and max length.
    """
    if any(
        [
            len(plain_text_password) < settings.DEFAULT_NEW_PASSWORD_MIN_LENGTH,
            len(plain_text_password) > settings.DEFAULT_NEW_PASSWORD_MAX_LENGTH,
            check_digit(plain_text_password) < settings.DEFAULT_NEW_PASSWORD_MIN_DIGITS,
            check_special_chars(plain_text_password) is False,
        ]
    ):
        return False
    return True


def check_password_input(current_user_password, password, password_check):
    """
    Description: used when user update his password. We check if input is blank.
    """
    if any(
        [
            current_user_password == "",
            password == "",
            password_check == "",
        ]
    ):
        return False
    return True
