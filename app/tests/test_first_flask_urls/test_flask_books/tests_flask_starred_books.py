"""
All the tests functions for the starred books urls.
Notice that by default we already add dummies data through the application utils module.
"""


from sqlalchemy.orm import joinedload

from app.packages.database.models.models import Book, User


def test_get_user_starred_books_without_being_authenticated(client):
    """
    Description: check access to user's starred book page without being authenticated.
    """
    response = client.get(
        "http://localhost/front/users/2/starred/",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_get_user_starred_books_being_authenticated(client, access_session):
    """
    Description: check access to user's starred book page being authenticated.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "http://localhost/front/users/2/starred/",
        headers=headers,
    )
    assert response.status_code == 200
    assert b"LES FAVORIS DE" in response.data


def test_get_unexisting_user_starred_books_being_authenticated(client, access_session):
    """
    Description: get an unexisting user starred books page, without being authenticated.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "http://localhost/front/users/55555/starred/",
        headers=headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Utilisateur id 55555 inexistant" in response.data


def test_get_user_starred_books_for_other_user_being_authenticated(client, access_session):
    """
    Description: get the starred books page, being authenticated, for a different user.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "http://localhost/front/users/4/books/1/starred/add/",
        headers=headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous ne pouvez ajouter que vos favoris" in response.data


def test_get_user_starred_books_without_being_authenticated(client):
    """
    Description: get the current user starred books page, without being authenticated.
    """
    response = client.get(
        "http://localhost/front/users/2/books/1/starred/add/",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_get_user_starred_books_for_starred_book_being_authenticated(
        client, access_session
    ):
    """
    Description: get the starred books page, being authenticated, with book already starred.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "http://localhost/front/users/2/books/1/starred/add/",
        headers=headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous avez deja ce livre en favori" in response.data


def test_add_a_starred_book_for_unexisting_book_being_authenticated(
        client, access_session, get_flask_csrf_token
    ):
    """
    Description: get the starred books page, being authenticated, for unexisting book.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    form = {
        "user_id": "2",
        "book_id": "55555",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "http://localhost/front/users/2/books/55555/starred/add/",
        headers=headers,
        data=form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Livre inexistant" in response.data


def test_add_a_starred_book_to_user_being_authenticated(
    client, access_session, get_flask_csrf_token
):
    """
    Description: asks to add a starred book for current user, being authenticated.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }

    form = {
        "user_id": "2",
        "book_id": "4",
        "csrf_token": get_flask_csrf_token,
    }

    url = "http://localhost/front/users/2/books/4/starred/add/"
    response = client.post(url, data=form, headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"Livre en favori" in response.data


def test_delete_starred_book_for_unexisting_user_being_authenticated(
        client, access_session
    ):
    """
    Description: get the delete starred book page, being authenticated, with unexisting user.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "/front/users/55555/books/1/starred/delete/",
        headers=headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Utilisateur inexistant" in response.data


def test_delete_starred_book_for_other_user_being_authenticated(
        client, access_session
    ):
    """
    Description: get the delete starred book page, being authenticated, with different user.
    """
    headers = {
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "/front/users/3/books/1/starred/delete/",
        headers=headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous ne pouvez supprimer que vos favoris" in response.data


def test_delete_starred_book_with_unexisting_book_being_authenticated(
        client, access_session, get_flask_csrf_token
    ):
    """
    Description: delete unexisting starred book, being authenticated.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    form = {
        "user_id": "2",
        "book_id": "55555",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/users/2/books/55555/starred/delete/",
        headers=headers,
        data=form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Favori inexistant" in response.data


def test_delete_starred_book_being_authenticated(
        client, access_session, get_flask_csrf_token
    ):
    """
    Description: delete starred book, being authenticated.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    form = {
        "user_id": "2",
        "book_id": "1",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/users/2/books/3/starred/delete/",
        headers=headers,
        data=form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Favori supprim\xc3\xa9" in response.data
