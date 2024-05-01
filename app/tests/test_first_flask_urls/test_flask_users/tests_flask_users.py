"""
All the tests functions for the users urls.
Notice that by default we already add dummies data through the application utils module.
"""


from app.packages.database.models.models import User
from app.packages.flask_app.project.__init__ import format_user
from app.packages import settings


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


def test_get_current_user_books(client, access_session):
    """
    Description: check if we can get all published books by an user. Try with dummy user id 2 (donald).
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/user/2/books/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - VOS LIVRES' in response.data


def test_get_any_valid_user_books(client, access_session):
    """
    Description: check if we can get all published books by a valid user.
    Try with dummy user id 3 (daisy).
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/user/3/books/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - LIVRES DE ' in response.data


def test_get_invalid_user_books(client, access_session):
    """
    Description: check if we can get all published books by an invalid user.
    Try with dummy user id 55555555.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/user/55555555/books/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'Utilisateur id 55555555 inexistant' in response.data


def test_flask_get_delete_user(client):
    """
    Description: check if we can reach the delete user route with GET method
    """
    response = client.get(
        "http://localhost/front/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


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


def test_flask_post_delete_user_without_authentication(client):
    """
    Description: check if we can reach the delete user route without authentication
    """
    response = client.post(
        "http://localhost/front/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 400


def test_flask_post_delete_user_with_authentication_as_admin(
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


def test_flask_post_delete_user_with_authentication_without_being_admin(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we delete user route without being authenticated as admin
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "http://localhost/front/user/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403


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


def test_get_users_without_being_admin(client, access_session):
    """
    Description: check if we can get users uri without being admin.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/users/", headers=headers, follow_redirects=True)
    assert response.status_code == 403


def test_get_users_being_admin(client, access_session_as_admin):
    """
    Description: check if we can get users uri without being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.get("/front/users/", headers=headers, follow_redirects=True)
    assert response.status_code == 200


def test_add_user_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can create an user without being admin.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 403


# def test_add_user_being_admin(
#     client,
#     access_session_as_admin,
#     get_flask_csrf_token,
# ):
#     """
#     Description: check if we can create an user without being admin.
#     """
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     data = {
#         "login": "dupond",
#         "password": settings.TEST_USER_PWD[:5],
#         "password_check": settings.TEST_USER_PWD[:5],
#         "email": "dupond@localhost.fr",
#         "csrf_token": get_flask_csrf_token,
#     }
#     response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
#     assert b"Mot de passe trop simple" in response.data


def test_add_invalid_email_user_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can create a valid user being admin.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 403


# def test_add_invalid_password_user_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can create an invalid user due to password, being admin.
#     """
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     data = {
#         "login": "dupond",
#         "password": f"{settings.TEST_USER_PWD}xxx",
#         "password_check": settings.TEST_USER_PWD,
#         "email": "dupond@localhost.fr",
#         "csrf_token": get_flask_csrf_token,
#     }
#     response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Mots de passe ne correspondent pas" in response.data


# def test_add_invalid_email_user_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can create an invalid user due to email, being admin.
#     """
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     data = {
#         "login": "dupond",
#         "password": f"{settings.TEST_USER_PWD}",
#         "password_check": settings.TEST_USER_PWD,
#         "email": "donald@localhost.fr",
#         "csrf_token": get_flask_csrf_token,
#     }
#     response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Email existe deja en base" in response.data
#
#
# def test_add_invalid_username_user_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can create an invalid user due to username, being admin.
#     """
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     data = {
#         "login": "donald",
#         "password": f"{settings.TEST_USER_PWD}",
#         "password_check": settings.TEST_USER_PWD,
#         "email": "dupond@localhost.fr",
#         "csrf_token": get_flask_csrf_token,
#     }
#     response = client.post("/front/users/add/", headers=headers, data=data, follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Nom utilisateur existe deja, veuillez le modifier" in response.data
