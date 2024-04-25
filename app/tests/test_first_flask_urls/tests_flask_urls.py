"""
All the tests functions for the flask urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
try:
    from app.packages.database.models.models import Book, User, BookCategory
    from app.packages.flask_app.project.__init__ import check_book_fields, check_book_category_fields
    from app.packages import settings
except ModuleNotFoundError:
    from packages.database.models.models import Book, User, BookCategory
    from packages.flask_app.project.__init__ import check_book_fields, check_book_category_fields
    from packages import settings


def test_flask_weird_route(client):
    """
    Description: check if we can reach an unexisting url
    """
    response = client.get("http://localhost/weird_uri")
    assert response.status_code == 404


def test_flask_index_route_without_rewrite_url(client):
    """
    Description: check if we can reach the index route
    """
    response = client.get("http://localhost/front")
    assert response.status_code == 200


def test_flask_index_route(client):
    """
    Description: check if we can reach the index route
    """
    response = client.get("http://localhost/front/home/")
    assert response.status_code == 200
    assert b"DUMMY BLOG" in response.data


def test_flask_ops_route(client):
    """
    Description: check if we can reach the ops route
    """
    response = client.get("http://localhost/front/ops/")
    assert response.status_code == 200
    assert b"DUMMY BLOG - OPS" in response.data


def test_flask_moocs_route(client):
    """
    Description: check if we can reach the moocs route
    """
    response = client.get("http://localhost/front/moocs/")
    assert response.status_code == 200
    assert b"DUMMY BLOG - MOOCS" in response.data


def test_flask_contact_route(client):
    """
    Description: check if we can reach the contact route
    """
    response = client.get("http://localhost/front/contact/")
    assert response.status_code == 200
    assert b"DUMMY BLOG - CONTACTEZ NOUS" in response.data


def test_flask_books_route(client):
    """
    Description: check if we can reach the books route
    """
    response = client.get("http://localhost/front/books/")
    assert response.status_code == 200
    assert b'class="post-title">Au commencement' in response.data
