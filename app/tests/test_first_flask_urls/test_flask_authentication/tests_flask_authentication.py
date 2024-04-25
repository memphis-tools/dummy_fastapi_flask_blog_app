"""
All the tests functions for the authentication urls.
Notice that by default we already add dummies data through the application utils module.
"""

try:
    from app.packages.database.models.models import Book, User
    from app.packages import settings
except ModuleNotFoundError:
    from packages.database.models.models import Book, User
    from packages import settings


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


def test_flask_login_with_valid_credentials(client, get_flask_csrf_token):
    """
    Description: check the login
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "daisy",
        "email": "daisy@localhost.fr",
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
        "login": "daisy",
        "email": "daisy@localhost.fr",
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
