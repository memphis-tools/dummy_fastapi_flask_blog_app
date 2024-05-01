""" check password againt a policy """


from flask import Flask, url_for, render_template, flash, abort, redirect, request, Response
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
    return all([
        special_chars_count >= settings.DEFAULT_NEW_PASSWORD_MIN_SPECIAL_CHAR,
        forbidden_chars_count == 0,
    ])


def check_password(plain_password):
    """
    Description: check if password respects the min and max length.
    """
    if any([
        len(plain_password) < settings.DEFAULT_NEW_PASSWORD_MIN_LENGTH,
        len(plain_password) > settings.DEFAULT_NEW_PASSWORD_MAX_LENGTH,
        check_digit(plain_password) < settings.DEFAULT_NEW_PASSWORD_MIN_DIGITS,
        check_special_chars(plain_password) is False,
    ]):
        return False
    return True
