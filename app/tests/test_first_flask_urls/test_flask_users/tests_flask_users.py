"""
All the tests functions for the users urls.
Notice that by default we already add dummies data through the application utils module.
"""

from app.packages.database.commands import session_commands
from app.packages.database.models.models import User
from app.packages import settings


def test_flask_get_users_without_authentication(client):
    """
    Description: check if we can reach a users page without authentication
    """
    response = client.get("/users/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_users_without_authentication_following_redirect(client):
    """
    Description: check if we can reach a users page without authentication
    """
    response = client.get("/users/", follow_redirects=True)
    assert response.status_code == 200


def test_get_current_user_books(client, access_session):
    """
    Description: check if we can get all published books by an user. Try with dummy user id 2 (donald).
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "/user/2/books/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"DUMMY OPS - VOS LIVRES" in response.data


def test_get_any_valid_user_books(client, access_session):
    """
    Description: check if we can get all published books by a valid user.
    Try with dummy user id 3 (daisy).
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "/user/3/books/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"DUMMY OPS - LIVRES DE " in response.data


def test_get_invalid_user_books(client, access_session):
    """
    Description: check if we can get all published books by an invalid user.
    Try with dummy user id 55555555.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "/user/55555555/books/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Utilisateur id 55555555 inexistant" in response.data


def test_flask_get_delete_user(client):
    """
    Description: check if we can reach the delete user route with GET method
    """
    response = client.get(
        "/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 302


def test_flask_post_users(client):
    """
    Description: check if we can reach the delete user route with POST method
    """
    response = client.post("/users/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_put_users(client):
    """
    Description: check if we can reach the user route with PUT method
    """
    response = client.put("/users/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_delete_users(client):
    """
    Description: check if we can reach the user route with DELETE method
    """
    response = client.delete("/users/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_delete_user_without_authentication(client):
    """
    Description: check if we can reach the delete user route without authentication
    """
    response = client.post(
        "/user/1/delete/", follow_redirects=False
    )
    assert response.status_code == 400


def test_flask_delete_user_with_authentication_as_admin(
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
        "/user/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_flask_delete_user_with_authentication_without_being_admin(
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
        "/user/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403


def test_flask_delete_user_admin_with_authentication(
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
        "/user/1/delete/",
        headers=headers,
        data=data,
        follow_redirects=True,
    )
    assert response.status_code == 403


def test_get_users_without_being_admin(client, access_session):
    """
    Description: check if we can get users uri without being admin.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get("/users/", headers=headers, follow_redirects=True)
    assert response.status_code == 403


def test_get_users_being_admin(client, access_session_as_admin):
    """
    Description: check if we can get users uri being admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get("/users/", headers=headers, follow_redirects=True)
    assert response.status_code == 200


def test_get_users_from_database_as_admin():
    """
    Description: check if we can request the database in order to get all users as admin.
    Notice that we set dummies datas to be test. We exclude admin user from request.
    """
    session = session_commands.get_a_database_session()
    all_users = session.query(User).all()[1:]
    session.close()
    assert len(all_users) > 1


def test_add_user_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can create an user without being admin.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/add/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 403


def test_add_user_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token,
):
    """
    Description: check if we can create an user being admin.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD[:5],
        "password_check": settings.TEST_USER_PWD[:5],
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/add/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200


def test_add_invalid_email_user_without_being_admin(
    client, access_session, get_flask_csrf_token
):
    """
    Description: check if we can create a valid user being admin.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/add/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 403


def test_add_user_with_unmatching_passwords_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can create an user with unmatching passwords being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    data = {
        "login": "dupond",
        "password": f"{settings.TEST_USER_PWD}xyz",
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post("/users/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 200


def test_add_user_with_existing_email_being_admin(
    client, access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can create an user with existing email being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    data = {
        "login": "dupond",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "email": "donald@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post("/users/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 200


def test_add_user_with_existing_username_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can create an user with existing username, being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    data = {
        "login": "donald",
        "password": f"{settings.TEST_USER_PWD}",
        "password_check": settings.TEST_USER_PWD,
        "email": "dupond@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post("/users/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 200


def test_update_user_password_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user being admin.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200


def test_update_user_password_being_legitimate_user(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user being the legitimate user.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Mot de passe mis a jour" in response.data


def test_update_user_password_being_legitimate_user_with_wrong_current_password(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with wrong current password.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": f"{settings.TEST_USER_PWD}123456789",
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Mot de passe actuel ne correspond pas" in response.data


def test_update_user_password_being_legitimate_user_with_blank_current_password(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with blank current password.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": "",
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200


def test_update_user_password_being_legitimate_user_with_blank_new_password(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with blank new password.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": "",
        "new_password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200


def test_update_user_password_being_legitimate_user_with_blank_new_password_check(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with blank new_password_check.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": "",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200


def test_update_user_password_being_legitimate_user_with_uncomplex_new_password(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with uncomplex new password.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}[:5]",
        "new_password_check": f"{settings.TEST_USER_PWD}[:5]",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Mot de passe trop simple" in response.data


def test_update_user_password_being_legitimate_user_with_mismatched_new_passwords(
    client,
    access_session,
    get_flask_csrf_token,
):
    """
    Description: check if we can update an existing user with mismatch new passwords.
    Notice we allow update even if password still the same.
    """
    headers = {"Cookie": f"session={access_session}"}
    data = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}",
        "new_password_check": f"{settings.TEST_USER_PWD}bebopalula",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/users/password/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Mots de passes ne correspondent pas" in response.data
