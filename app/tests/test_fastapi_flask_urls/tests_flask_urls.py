"""
All the tests functions for the status from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
try:
    from app.packages.database.models.models import Book, User
    from app.packages.flask_app.project.__init__ import check_book_fields
    from app.packages import settings
except ModuleNotFoundError:
    from packages.database.models.models import Book, User
    from packages.flask_app.project.__init__ import check_book_fields
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


def test_flask_login_route(client):
    """
    Description: check if we can reach the login route
    """
    response = client.get("http://localhost/front/login/")
    assert response.status_code == 200
    assert b"DUMMY BLOG - SE CONNECTER" in response.data


def test_flask_post_logout_route_without_authentication(client):
    """
    Description: check if we can reach the logout route with POST action.
    """
    response = client.post("http://localhost/front/logout/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_post_logout_route_with_authentication(
    client, access_session,
):
    """
    Description: check if we can reach the logout route
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "http://localhost/front/logout/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


def test_flask_logout_route_without_authentication(client):
    """
    Description: check if we can reach the logout route
    """
    response = client.get("http://localhost/front/logout/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_logout_route_without_authentication_following_redirect(client):
    """
    Description: check if we can reach the logout route
    """
    response = client.get("http://localhost/front/logout/", follow_redirects=True)
    assert response.status_code == 200


def test_flask_register_route(client):
    """
    Description: check if we can reach the register route
    """
    response = client.get("http://localhost/front/register/")
    assert response.status_code == 200


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


def test_flask_get_users_without_authentication(client):
    """
    Description: check if we can reach a users page without authentication
    """
    response = client.get("http://localhost/front/users/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_users_without_authentication_following_redirect(client):
    """
    Description: check if we can reach a users page without authentication
    """
    response = client.get("http://localhost/front/users/", follow_redirects=True)
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

    url = "http://localhost/front/add_book/"
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

    url = "http://localhost/front/add_book/"
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

    url = "http://localhost/front/add_book/"
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

    url = "http://localhost/front/add_book/"
    response = client.post(url, data=book_form, headers=headers, follow_redirects=True)
    assert response.status_code == 400


def test_flask_update_book_being_authenticated(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can update a book.
    """

    book_form = {
        "title": "This is a dummy title sir",
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


def test_post_flask_register_route(client, get_flask_csrf_token):
    """
    Description: check if we can register new user
    """
    user_form = {
        "login": "fafa",
        "email": "fafa@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/front/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Bienvenue fafa vous pouvez vous connecter" in response.data


def test_post_flask_register_route_with_existing_email(client, get_flask_csrf_token):
    """
    Description: check if we can register new user with an already existing email
    """
    user_form = {
        "login": "leon",
        "email": "daisy@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/front/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Email existe deja en base" in response.data


def test_post_flask_register_route_with_passwords_mismatch(
    client, get_flask_csrf_token
):
    """
    Description: check if we can register new user with mismatched passwords
    """
    user_form = {
        "login": "leon",
        "email": "leon@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": "dummypassword",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/front/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mots de passe ne correspondent pas" in response.data


def test_post_flask_register_route_with_existing_user(client, get_flask_csrf_token):
    """
    Description: check if we can register new user with an already existing username
    """
    user_form = {
        "login": "donald",
        "email": "leon@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/front/register/",
        headers=headers,
        data=user_form,
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"Nom utilisateur existe deja, veuillez le modifier" in response.data


def test_post_flask_register_route_with_invalid_data(client):
    """
    Description: check if we can register new user
    """
    user_form = {
        "login": "fafa",
        "email": "fafa@localhost.fr",
        "password": settings.TEST_USER_PWD,
    }
    response = client.post(
        "http://localhost/front/register/", headers="", data=user_form
    )
    assert response.status_code == 400


def test_flask_get_delete_book(client):
    """
    Description: check if we can reach the delete book route with GET method
    """
    response = client.get(
        "http://localhost/front/book/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_get_delete_comment(client):
    """
    Description: check if we can reach the delete comment route with GET method
    """
    response = client.get(
        "http://localhost/front/comment/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_get_delete_user(client):
    """
    Description: check if we can reach the delete user route with GET method
    """
    response = client.get(
        "http://localhost/front/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_post_books(client):
    """
    Description: check if we can reach the delete book route with POST method
    """
    response = client.post("http://localhost/front/books/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_post_comments(client):
    """
    Description: check if we can reach the delete comment route with POST method
    """
    response = client.post("http://localhost/front/comments/", follow_redirects=True)
    assert response.status_code == 404


def test_flask_post_users(client):
    """
    Description: check if we can reach the delete user route with POST method
    """
    response = client.post("http://localhost/front/users/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_put_users(client):
    """
    Description: check if we can reach the user route with PUT method
    """
    response = client.put("http://localhost/front/users/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_delete_users(client):
    """
    Description: check if we can reach the user route with DELETE method
    """
    response = client.delete("http://localhost/front/users/", follow_redirects=True)
    assert response.status_code == 405


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
        "http://localhost/front/book/7/delete/",
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


def test_flask_post_delete_user_without_authentication(client):
    """
    Description: check if we can reach the delete user route without authentication
    """
    response = client.post(
        "http://localhost/front/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 400


def test_flask_post_delete_user_with_authentication(
    client, access_session_as_admin, get_flask_csrf_token
):
    """
    Description: check if we delete user route being authenticated as admin
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/front/user/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_flask_post_delete_user_admin_with_authentication(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can delete user admin being authenticated.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/front/user/1/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403


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
        "categories-0-intitule": "histoire",
        "author": "Dummy Boy",
        "photo": FileStorage(
            stream=(resources / "photo_pexels.com_by_inga_seliverstova.jpg").open("rb"),
            filename="photo_pexels.com_by_inga_seliverstova.jpg",
            content_type="image/jpeg",
        ),
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/add_book/",
        headers=headers,
        data=book_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Saisie invalide, mot clef string non utilisable" in response.data


def test_check_book_fields(access_session):
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


def test_flask_login_with_valid_credentials(client, get_flask_csrf_token):
    """
    Description: check the login
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "donald",
        "email": "donald@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous nous avez manq" in response.data

def test_flask_login_with_invalid_login(client, get_flask_csrf_token):
    """
    Description: check the login with invalid login
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "tintin",
        "email": "donald@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Identifiants invalides" in response.data


def test_flask_login_with_invalid_email(client, get_flask_csrf_token):
    """
    Description: check the login with invalid email
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "donald",
        "email": "tintin@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Identifiants invalides" in response.data


def test_flask_login_with_invalid_password(client, get_flask_csrf_token):
    """
    Description: check the login with invalid password
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "donald",
        "email": "donald@localhost.fr",
        "password": "bebopalula",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/front/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mot de passe invalide" in response.data


def test_flask_get_logout(client, access_session):
    """
    Description: check if logout works.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("http://localhost/front/logout/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"plus connect" in response.data
