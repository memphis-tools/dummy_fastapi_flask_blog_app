"""
All the tests functions for the books urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest
from pathlib import Path
from werkzeug.datastructures import FileStorage

from app.packages.database.models.models import Book, User
from app.packages.flask_app.project.__init__ import check_book_fields, get_pie_colors
from app.packages import settings


def test_flask_get_a_book_without_authentication(client):
    """
    Description: check if we can reach a book page without authentication
    """
    response = client.get("http://localhost/front/book/1/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_a_book_without_authentication_following_redirect(client):
    """
    Description: check if we can reach a book page without authentication
    """
    response = client.get("http://localhost/front/book/1/", follow_redirects=True)
    assert response.status_code == 200


def test_flask_post_add_book_with_authentication(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can add a book being authenticated and without following redirect.
    """
    # get the resources folder in the tests folder
    #rb flag means "Open in binary mode (read/write using byte data)" - https://realpython.com/read-write-files-python/
    resources = Path(__file__).parent
    headers = {
        "Content-Type": "multipart/form-data",
        "Cookie": f"session={access_session}",
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

    url = "http://localhost/front/books/add/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 200


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

    url = "http://localhost/front/books/add/"
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

    url = "http://localhost/front/books/add/"
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

    url = "http://localhost/front/books/add/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 400


def test_flask_get_delete_book(client):
    """
    Description: check if we can reach the delete book route with GET method
    """
    response = client.get(
        "http://localhost/front/book/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_post_books(client):
    """
    Description: check if we can reach the delete book route with POST method
    """
    response = client.post("http://localhost/front/books/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_update_book_being_authenticated(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a book.
    """

    book_form = {
        "title": "This is a dummy title sir",
        "categories": "1",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "http://localhost/front/book/1/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200


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
        "http://localhost/front/book/update/",
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
        "http://localhost/front/book/2/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 403


def test_flask_update_book_being_authenticated_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we can update a book being admin.
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
        "http://localhost/front/book/2/update/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200


# def test_flask_update_unexisting_book_being_authenticated_as_admin(
#     client, access_session_as_admin, get_flask_csrf_token
# ):
#     """
#     Description: check if we can update an unexisting book being admin.
#     """
#
#     book_form = {
#         "title": "This is a dummy title sir",
#         "categories": "1",
#         "csrf_token": get_flask_csrf_token,
#     }
#
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Cookie": f"session={access_session_as_admin}",
#     }
#     response = client.post(
#         "http://localhost/front/book/55555555/update/",
#         headers=headers,
#         data=book_form,
#         follow_redirects=True,
#     )
#     assert b"Livre non trouv" in response.data


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
        "http://localhost/front/book/1/update/",
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
        "http://localhost/front/book/1/delete/",
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
        "http://localhost/front/book/2/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403
    assert b"You don&#39;t have the permission to access the requested resource." in response.data


def test_flask_post_delete_book_being_authenticated_being_the_publisher(
    client, access_session,
    get_flask_csrf_token,
    get_session,
    mock_function_delete_book,
):
    """
    Description: check if we can delete book route being authenticated being the book's publisher.
    See utils.py to discover all dummy datas set.
    Here 1 book published by user id 2 (the one which has the 'get_session') has already been deleted (tests_routes.py)
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    book = get_session.get(Book, 8)
    user = get_session.get(User, book.user_id)
    current_user_total_publications = user.nb_publications
    assert current_user_total_publications == 2

    response = client.post(
        "http://localhost/front/book/8/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    get_session.refresh(user)
    assert user.nb_publications == current_user_total_publications - 1


def test_add_book_check_book_fields(
    client,
    access_session,
    get_flask_csrf_token
):
    """
    Description: check if we can add a book with 'string' keyword as content.
    """
    # get the resources folder in the tests folder
    #rb flag means "Open in binary mode (read/write using byte data)" - https://realpython.com/read-write-files-python/
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
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.jpg").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.jpg",
            content_type="image/jpeg",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/books/add/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saisie invalide, mot clef string non utilisable" in response.data


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
    assert type(response) is list
