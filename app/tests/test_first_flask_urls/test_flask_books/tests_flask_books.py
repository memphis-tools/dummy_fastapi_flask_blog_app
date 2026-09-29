"""
All the tests functions for the books urls.
Notice that by default we already add dummies data through the application utils module.
"""

import html
import pytest
from pathlib import Path
from werkzeug.datastructures import FileStorage
from bs4 import BeautifulSoup
from sqlalchemy.orm import joinedload
from app.packages.database.models.models import Book, User
from app.packages.flask_app.project.shared_functions_and_decorators import get_pie_colors
from app.packages.flask_app.project.book_routes_blueprint import check_book_fields


def test_flask_get_an_unknow_book_without_authentication(client):
    """
    Description: check if we can reach an unknow book page without authentication
    """
    response = client.get("http://localhost/book/55555/", follow_redirects=True)
    assert "Vous devez d&#39;abord vous connecter" in response.text
    assert response.status_code == 200


def test_flask_get_an_unknow_book_being_authenticated(
    client, access_session
):
    """
    Description: check if we can reach an unknow book page being authenticated
    """
    response = client.get("http://localhost/book/55555/", follow_redirects=True)
    assert "Livre id 55555 inexistant" in response.text
    assert response.status_code == 200


def test_flask_get_a_book_without_authentication(client):
    """
    Description: check if we can reach a book page without authentication
    """
    response = client.get("http://localhost/book/1/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_a_book_without_authentication_following_redirect(client):
    """
    Description: check if we can reach a book page without authentication
    """
    response = client.get("http://localhost/book/1/", follow_redirects=True)
    assert response.status_code == 200


def test_flask_post_add_book_with_bad_category_with_authentication(
    client, access_session
):
    """
    Description:
    Check if we can add a book being authenticated with non existing category.
    """
    # get the resources folder in the tests folder
    # rb flag means "Open in binary mode (read/write using byte data)" - https://realpython.com/read-write-files-python/
    resources = Path(__file__).parent

    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "author": "Dummy Sapiens",
        "categories": "99999999999998888888888888777777777777777777777777777777",
        "year_of_publication": "1999",
        "photo": (resources / "photo_pexels.com_by_inga_seliverstova.jpg").open(
            "rb"
        ),
        "csrf_token": csrf_token,
    }
    with pytest.raises(Exception):
        response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
        assert response.status_code == 200
        assert "Saisie invalide, categorie livre non prevue" in response.data


def test_flask_post_add_book_with_forbidden_image_format_with_authentication(
    client, access_session
):
    """
    Description: check if we can add a book being authenticated, with a bad image format.
    """
    # get the resources folder in the tests folder
    # rb flag means "Open in binary mode (read/write using byte data)" - https://realpython.com/read-write-files-python/
    resources = Path(__file__).parent

    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "author": "Dummy Sapiens",
        "categories": "2",
        "year_of_publication": "1999",
        "photo": (resources / "wrong_image.jpg").open(
            "rb"
        ),
        "csrf_token": csrf_token,
    }
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"Type image non accept\xc3\xa9" in response.data


def test_flask_post_add_book_with_authentication(
    client, access_session
):
    """
    Description: check if we can add a book being authenticated and without following redirect.
    """
    # get the resources folder in the tests folder
    # rb flag means "Open in binary mode (read/write using byte data)" - https://realpython.com/read-write-files-python/
    resources = Path(__file__).parent

    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "author": "Dummy Sapiens",
        "categories": "2",
        "year_of_publication": "1999",
        "photo": (resources / "photo_pexels.com_by_inga_seliverstova.jpg").open(
            "rb"
        ),
        "csrf_token": csrf_token,
    }
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"Livre ajout\xc3\xa9." in response.data


def test_flask_post_add_book_without_authentication(client, get_flask_csrf_token):
    """
    Description: check if we can add a book being authenticated.
    """
    # get the resources folder in the tests folder
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "author": "Dummy Sapiens",
        "book_picture": (resources / "photo_pexels.com_by_inga_seliverstova.jpg").open(
            "rb"
        ),
        "csrf_token": get_flask_csrf_token,
    }

    url = "http://localhost/books/add/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_flask_post_add_book_without_authentication_with_invalid_datas(client):
    """
    Description: check if we can add a book without being authenticated and without a csrf token.
    """
    headers = {"Content-Type": "multipart/form-data"}
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
    }

    url = "http://localhost/books/add/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 400


def test_flask_post_add_book_without_authentication_with_invalid_book_category(client):
    """
    Description: check if we can add a book without being authenticated and without a csrf token.
    """
    headers = {"Content-Type": "multipart/form-data"}
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "category": "supplication"
    }

    url = "http://localhost/books/add/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 400


def test_flask_get_delete_book(client):
    """
    Description: check if we can reach the delete book route with GET method
    """
    response = client.get(
        "http://localhost/book/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_post_books(client):
    """
    Description: check if we can reach the delete book route with POST method
    """
    response = client.post("http://localhost/books/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_update_book_being_authenticated(
    client, access_session
):
    """
    Description: check if we can update a book.
    """

    url = "http://localhost/book/1/update/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    book_form = {
        "title": "This is a dummy title sir",
        "categories": "1",
        "csrf_token": csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "http://localhost/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mise \xc3\xa0 jour livre." in response.data


def test_flask_update_book_being_authenticated_without_book_id(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a book without specifying a book id.
    """

    book_form = {
        "title": "This is a dummy title sir",
        "category": "1",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "http://localhost/book/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 404


def test_flask_update_book_being_authenticated_without_being_publisher(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a book which user has not published.
    """

    book_form = {
        "title": "This is a dummy title sir",
        "category": "1",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "http://localhost/book/2/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 403


def test_flask_update_book_being_authenticated_as_admin(
    client, access_session_as_admin
):
    """
    Description: check if we can update a book being admin.
    """
    url = "http://localhost/book/2/update/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    book_form = {
        "title": "This is a dummy title sir",
        "categories": "1",
        "csrf_token": csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}",
    }
    response = client.post(
        "http://localhost/book/2/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mise \xc3\xa0 jour livre." in response.data


def test_flask_update_unexisting_book_being_authenticated_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we can update an unexisting book being admin.
    """

    book_form = {
        "title": "This is a dummy title sir",
        "categories": "1",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}",
    }
    response = client.post(
        "http://localhost/book/55555555/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert b"Livre non trouv" in response.data
    assert response.status_code == 200


def test_flask_update_book_without_authentication(client, get_flask_csrf_token):
    """
    Description: check if we can update a book.
    """
    book_form = {
        "title": "This is a dummy title sir",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = client.post(
        "http://localhost/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_flask_post_delete_book_without_authentication(client, get_flask_csrf_token):
    """
    Description: check if we can delete book route without authentication
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/book/1/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_flask_post_delete_book_being_authenticated_without_being_the_publisher(
    client, access_session, get_flask_csrf_token,
):
    """
    Description: check if we can delete book route being authenticated without being the book's publisher.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/book/2/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403
    assert b"You don&#39;t have the permission to access the requested resource." in response.data


def test_flask_post_delete_book_being_authenticated_being_the_publisher(
    client, access_session,
    get_session,
    mock_function_delete_book,
):
    """
    Description: check if we can delete book route being authenticated being the book's publisher.
    See utils.py to discover all dummy datas set.
    Here 1 book published by user id 2 (the one which has the 'get_session') has already been deleted (tests_routes.py)
    """
    url = "http://localhost/book/8/delete/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": csrf_token}
    book = get_session.get(Book, 8)
    user = get_session.query(User).filter(
        User.id == book.user_id
    ).options(
        joinedload(User.books)
    ).one()
    current_user_total_publications = len(user.books)
    assert current_user_total_publications == 4

    response = client.post(
        "http://localhost/book/8/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    get_session.refresh(user)
    assert len(user.books) == current_user_total_publications - 1


def test_check_book_fields():
    """
    Description: check the book's year of publication.
    """
    new_book = Book(
        title="This is a dummy title sir",
        summary="This is a dummy summary sir",
        content="This is a dummy content sir",
        author="This is a dummy author sir",
        category=1,
        year_of_publication="abcd",
        book_picture_name="dummy_filename.png",
        user_id=2,
    )
    response = check_book_fields(new_book)
    assert "Saisie invalide, annee publication livre doit etre un entier." == response


def test_get_pie_colors():
    """
    Description: check the get pie colors.
    """
    response = get_pie_colors()
    assert isinstance(response, list)


def test_flask_index_route_with_three_random_books(client, access_session):
    """
    Description: check if we get 3 books while more than 3 exist in database.
    By default 3 books are expected.
    """
    response = client.get("http://localhost/home/")
    soup = BeautifulSoup(response.data, "html.parser")
    total_books = len(soup.find_all("div", {"class": "post-preview"}))
    assert response.status_code == 200
    assert total_books == 3


def test_add_book_with_invalid_image_size(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice size limit is 5mo.
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "string",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.png").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.png",
            content_type="image/png",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/books/add/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 413
    assert b"Taille fichier exc\xc3\xa8de la limite pr\xc3\xa9vue" in response.data


def test_add_book_with_invalid_image_type(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice only types accepted: .jpg, .jpeg, .png
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "string",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.gif").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.gif",
            content_type="image/gif",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/books/add/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Seuls format autoris\xc3\xa9s: .jpg, .jpeg, .png" in response.data


def test_add_book_with_corrupted_image_type(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice only types accepted: .jpg, .jpeg, .png
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "dummy_image.png").open("rb"),
            filename="dummy_image.png",
            content_type="image/png",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/books/add/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_update_book_with_invalid_image_size(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice size limit is 5mo.
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.png").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.png",
            content_type="image/png",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 413


def test_update_book_with_invalid_image_type(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice only types accepted: .jpg, .jpeg, .png
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "string",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.gif").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.gif",
            content_type="image/gif",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Seuls format autoris\xc3\xa9s: .jpg, .jpeg, .png" in response.data


def test_update_book_with_corrupted_image_type(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with an invalid image type.
    Notice only types accepted: .jpg, .jpeg, .png
    """
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "year_of_publication": "2023",
        "categories": "3",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "dummy_image.png").open("rb"),
            filename="dummy_image.png",
            content_type="image/png",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200

# ------------------------------------------------------------------
# Supplementary tests proposed by Vibe (powered by glm-5-latest-short)
# on 2026-09-29 — v2: fixed module-shadowing monkeypatch paths,
# empty-filename form stub, flash patching (no request context).
# Goal: raise book_routes_blueprint.py coverage from 79% to max.
# ------------------------------------------------------------------
from importlib import import_module
from unittest.mock import MagicMock

from flask_wtf.file import FileField
from werkzeug.exceptions import HTTPException

from app.packages.flask_app.project import forms as project_forms
from app.packages.flask_app.project.book_routes_blueprint import (
    FileData,
    create_updated_book,
    get_book_by_id,
    get_category_id,
    get_updated_fields,
    handle_file_upload_and_removal,
    save_updated_book,
)


def _get_book_routes_blueprint_module():
    """
    Description: return the book_routes_blueprint MODULE. The project's
    __init__ shadows the module name with the Blueprint instance, so we
    go through import_module/sys.modules to get the real module object.
    """
    return import_module("app.packages.flask_app.project.book_routes_blueprint")


def test_flask_books_redirect_when_one_book(client, monkeypatch):
    """
    Description: covers line 81 -> 93: books() redirects to index when
    pagination returns 0 or 1 book. The dummy DB always has several books,
    so we mock return_pagination.
    """
    monkeypatch.setattr(
        _get_book_routes_blueprint_module(),
        "return_pagination",
        lambda items_to_paginate: ([], 1, 6, 1),
    )
    response = client.get("http://localhost/books/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_post_comment_on_a_book(client, access_session, get_session):
    """
    Description: covers line 146 -> 147: comment form submitted on book page.
    The created comment is removed at the end of the test.
    """
    from app.packages.database.models.models import Comment

    url = "http://localhost/book/1/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": csrf_token, "comment_text": "What a great dummy book sir!"}
    response = client.post(url, headers=headers, data=data, follow_redirects=False)
    assert response.status_code == 302

    # cleanup: remove the comment we just added
    comment = (
        get_session.query(Comment)
        .filter_by(text="What a great dummy book sir!", book_id=1)
        .first()
    )
    assert comment is not None
    get_session.delete(comment)
    get_session.commit()


def test_flask_post_add_book_with_invalid_fields(client, access_session):
    """
    Description: covers line 229 -> 261: check_book_fields returns an error
    (title keyword "string"), so the book is not added.
    """
    resources = Path(__file__).parent
    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "string",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "categories": "2",
        "year_of_publication": "1999",
        "author": "Dummy Sapiens",
        "photo": (resources / "photo_pexels.com_by_inga_seliverstova.jpg").open("rb"),
        "csrf_token": csrf_token,
    }
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"mot clef string non utilisable" in response.data
    assert b"Livre ajout\xc3\xa9." not in response.data


def _patch_book_form_photo_validators(monkeypatch):
    """
    Helper: replace BookForm with a subclass whose photo field has no
    FileRequired/FileAllowed validator, so we can post forbidden
    extensions through the route (the form blocks them otherwise).
    """

    class BookFormWithoutPhotoValidators(project_forms.BookForm):
        photo = FileField("IMAGE")

    monkeypatch.setattr(project_forms, "BookForm", BookFormWithoutPhotoValidators)


class _FakeField:
    def __init__(self, data):
        self.data = data


class _FakeBookForm:
    """
    A form stub bypassing CSRF/WTF validation so the route can run with a
    FileStorage whose filename is "" (an empty-filename upload never
    survives werkzeug parsing, so a real form cannot produce it).
    """

    def __init__(self, books_categories=None):
        resources = Path(__file__).parent
        self.title = _FakeField("This is a dummy title sir")
        self.summary = _FakeField("This is a dummy summary sir")
        self.content = _FakeField("This is a dummy content sir")
        self.author = _FakeField("Dummy Sapiens")
        self.categories = _FakeField("2")
        self.year_of_publication = _FakeField(1999)
        self.photo = _FakeField(
            FileStorage(
                stream=(resources / "photo_pexels.com_by_inga_seliverstova.jpg").open("rb"),
                filename="",
                content_type="image/jpeg",
            )
        )

    def validate_on_submit(self):
        return True


def test_flask_post_add_book_with_forbidden_extension_but_valid_image(
    client, access_session, monkeypatch
):
    """
    Description: covers line 232 -> 233 ("cas 2"): a valid image (PIL can open it)
    with a forbidden extension (.gif). The form validator is bypassed on purpose.
    """
    _patch_book_form_photo_validators(monkeypatch)
    resources = Path(__file__).parent
    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "categories": "2",
        "year_of_publication": "1999",
        "author": "Dummy Sapiens",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.gif").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.gif",
            content_type="image/gif",
        ),
        "csrf_token": csrf_token,
    }
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"cas 2" in response.data


def test_flask_post_add_book_in_production_scope(
    client, access_session, get_session, monkeypatch
):
    """
    Description: covers line 239 -> 240: SCOPE=production saves the uploaded
    file on disk. We mock FileStorage.save and the session factory so no
    file is written and no production DB connection is attempted.
    """
    monkeypatch.setenv("SCOPE", "production")
    monkeypatch.setattr(
        "app.packages.database.commands.session_commands.get_a_database_session",
        lambda: get_session,
    )
    monkeypatch.setattr(
        "werkzeug.datastructures.FileStorage.save",
        lambda self, dst, timeout=None: None,
    )
    resources = Path(__file__).parent
    url = "http://localhost/books/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
    }
    book_form = {
        "title": "This is a dummy production title sir",
        "summary": "This is a dummy summary sir",
        "content": "This is a dummy content sir",
        "categories": "2",
        "year_of_publication": "1999",
        "author": "Dummy Sapiens",
        "photo": (resources / "photo_pexels.com_by_inga_seliverstova.jpg").open("rb"),
        "csrf_token": csrf_token,
    }
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"Livre ajout\xc3\xa9." in response.data


def test_get_category_id_without_categories_key(get_session):
    """
    Description: covers line 359 -> 360: no "categories" key in form dict.
    """
    response = get_category_id({"title": "a title"}, get_session)
    assert response is None


def test_handle_file_upload_and_removal_with_dummy_picture():
    """
    Description: covers line 426 -> exit: filename is dummy_blank_book.png,
    so nothing is done.
    """
    result = handle_file_upload_and_removal("dummy_blank_book.png", "old.png", None)
    assert result is None


def test_handle_file_upload_and_removal_with_forbidden_extension():
    """
    Description: covers line 428 -> 429: forbidden extension aborts with 400.
    """
    with pytest.raises(HTTPException) as exc_info:
        handle_file_upload_and_removal("invalid_picture.txt", "old.png", None)
    assert exc_info.value.code == 400


def test_handle_file_upload_and_removal_in_production(monkeypatch):
    """
    Description: covers line 430 -> 431: in production the uploaded file is
    saved and the old picture removed (missing old file is ignored).
    """
    monkeypatch.setenv("SCOPE", "production")
    fake_uploaded_file = MagicMock()
    handle_file_upload_and_removal(
        "new_picture.jpg", "zzz_unexisting_picture.png", fake_uploaded_file
    )
    fake_uploaded_file.save.assert_called_once()
