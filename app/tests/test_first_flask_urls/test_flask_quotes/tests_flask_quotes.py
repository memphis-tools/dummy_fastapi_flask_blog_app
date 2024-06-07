"""
All the tests functions for the quotes urls.
Notice that by default we already add dummies data through the application utils module.
"""

from app.packages.database.commands import session_commands
from app.packages.database.models.models import Quote


def test_flask_get_quotes_without_authentication(client):
    """
    Description: check if we can reach a quotes page without authentication
    """
    response = client.get("http://localhost/quotes/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_quotes_without_authentication_following_redirect(client):
    """
    Description: check if we can reach a quotes page without authentication
    """
    response = client.get("http://localhost/quotes/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_get_quotes_as_a_standard_user(client, access_session):
    """
    Description: check if we can get all quotes as a standard user.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "/quotes/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 403


def test_get_a_quote_as_a_standard_user(client, access_session):
    """
    Description: check if we can get a quote as a standard user.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "/quotes/1/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 403


def test_get_quotes_as_admin(client, access_session_as_admin):
    """
    Description: check if we can get all quotes as admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get(
        "/quotes/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


def test_get_quotes_from_database_as_admin():
    """
    Description: check if we can request the database in order to get all quotes as admin.
    """
    session = session_commands.get_a_database_session()
    quotes = session.query(Quote).all()
    session.close()
    assert len(quotes) == 3


def test_get_a_quote_as_a_admin(client, access_session_as_admin):
    """
    Description: check if we can get a quote as admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get(
        "/quotes/1/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


def test_get_a_quote_from_database_as_admin():
    """
    Description: check if we can request the database in order to get a quote as admin.
    """
    session = session_commands.get_a_database_session()
    quote_to_view = session.get(Quote, 1)
    session.close()
    assert isinstance(quote_to_view, Quote)


def test_get_an_unexisting_quote_as_a_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can get an unexisting quote as admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    response = client.get(
        "/quotes/555555/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    # assert response.status_code == 404


def test_get_any_valid_quotes_for_deleting_as_admin(client, access_session_as_admin):
    """
    Description: check if we can delete a valid quote as admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get(
        "/quotes/1/delete/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


def test_add_a_valid_quote_as_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can add valid quote as admin.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    form = {
        "author": "bruce lee",
        "book_title": "be water",
        "quote": "be water my friend",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/quotes/add/",
        headers=headers,
        data=form,
        follow_redirects=True
    )
    assert response.status_code == 200
    # assert b'Ajout citation' in response.data


def test_add_an_invalid_quote_as_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can add invalid quote as admin.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    form = {
        "author": "bruce lee",
        "book_title": "be water",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/quotes/add/",
        headers=headers,
        data=form,
        follow_redirects=True
    )
    assert response.status_code == 200


def test_flask_delete_quote_without_authentication(client, access_session):
    """
    Description: check if we can delete a quote without authentication
    """
    response = client.post("http://localhost/quotes/2/delete/", follow_redirects=True)
    assert response.status_code == 400


def test_flask_delete_quote_as_standard_user(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can delete a quote as a standard user
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    form = {
        "Content-Type": "application/x-www-form-urlencoded",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "http://localhost/quotes/4/delete/",
        headers=headers,
        data=form,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_flask_delete_quote_with_authentication_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we delete a quote being authenticated as admin
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    form = {
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/quotes/4/delete/",
        headers=headers,
        data=form,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_flask_delete_unexisting_quote_with_authentication_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we raise an error trying to delete an unexisting quote
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/quotes/555555/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    # assert response.status_code == 404
