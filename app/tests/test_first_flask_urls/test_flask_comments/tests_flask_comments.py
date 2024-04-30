"""
All the tests functions for the comments urls.
Notice that by default we already add dummies data through the application utils module.
"""

try:
    from app.packages.database.models.models import Book
    from app.packages import settings
except ModuleNotFoundError:
    from packages.database.models.models import Book
    from packages import settings


def test_flask_get_delete_comment(client):
    """
    Description: check if we can reach the delete comment route with GET method
    """
    response = client.get(
        "http://localhost/front/comment/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_post_comments(client):
    """
    Description: check if we can reach the delete comment route with POST method
    """
    response = client.post("http://localhost/front/comments/", follow_redirects=True)
    assert response.status_code == 404


def test_flask_post_delete_comment_without_authentication(client):
    """
    Description: check if we can reach the delete comment route without authentication
    """
    response = client.post(
        "http://localhost/front/comment/1/delete/", headers="", follow_redirects=False
    )
    assert response.status_code == 400


def test_flask_post_delete_comment_with_authentication(
    client, access_session, get_flask_csrf_token, get_session
):
    """
    Description: check if we can delete comment route with authentication, as comment author.
    Notice that the the comment with id 2 is relative to the book which id is also 2 (see utils.py).
    The "get_session" fixture gives a session to query the database.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    book = get_session.get(Book, 2)
    current_total_comments = book.nb_comments
    assert current_total_comments == 1
    response = client.post(
        "http://localhost/front/comment/2/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200
    get_session.refresh(book)
    assert book.nb_comments == current_total_comments - 1


def test_flask_post_delete_comment_with_auth_without_being_author(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can delete comment route with authentication without being author.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/front/comment/1/delete/",
        headers=headers,
        data=data,
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_flask_post_delete_comment_with_auth_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we can delete comment route with authentication being admin.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/front/comment/1/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_flask_post_update_comment_without_being_logged_in(
    client, get_flask_csrf_token
):
    """
    Description: check if we can update a comment without being logged in.
    """
    user_form = {
        "comment": "this is an updated comment sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "/front/comment/1/update/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous devez d&#39;abord vous connecter" in response.data


def test_flask_post_update_comment_when_user_is_the_author(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a comment.
    """
    user_form = {
        "comment": "this is an updated comment sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "/front/comment/5/update/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Commentaire mis a jour" in response.data


def test_flask_post_update_comment_authenticated_without_comment_id(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a comment without specifying an id.
    """
    user_form = {
        "comment": "this is an updated comment sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "/front/comment/update/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 404


def test_flask_post_update_comment_when_user_is_not_the_author(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a comment.
    """
    user_form = {
        "comment": "this is an updated comment sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.post(
        "/front/comment/6/update/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 403


def test_flask_post_update_comment_as_admin(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we can update a comment as an admin.
    """
    user_form = {
        "comment": "this is an updated comment sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}",
    }
    response = client.post(
        "/front/comment/6/update/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
