"""
All the tests functions for the authentication urls.
Notice that by default we already add dummies data through the application utils module.
"""

import html
from app.packages import settings


def test_flask_login_route(client):
    """
    Description: check if we can reach the login route
    """
    response = client.get("http://localhost/login/")
    assert response.status_code == 200
    assert b"DUMMY OPS - SE CONNECTER" in response.data


def test_flask_post_logout_route_without_authentication(client):
    """
    Description: check if we can reach the logout route with POST action.
    """
    response = client.post("http://localhost/logout/", follow_redirects=True)
    assert response.status_code == 405


def test_flask_post_logout_route_with_authentication(
    client, access_session,
):
    """
    Description: check if we can reach the logout route
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get(
        "http://localhost/logout/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


def test_flask_logout_route_without_authentication(client):
    """
    Description: check if we can reach the logout route
    """
    response = client.get("http://localhost/logout/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_logout_route_without_authentication_following_redirect(client):
    """
    Description: check if we can reach the logout route
    """
    response = client.get("http://localhost/logout/", follow_redirects=True)
    assert response.status_code == 200


def test_flask_register_route(client):
    """
    Description: check if we can reach the register route
    """
    response = client.get("http://localhost/register/")
    assert response.status_code == 200


def test_flask_login_with_unactivated_account(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if user can login whereas account unactivated
    """
    user_form = {
        "login": "louloute",
        "email": "louloute@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/login/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Compte Louloute inactif." in response.data


def test_flask_login_with_unactivated_account_and_captcha_error(app, client, get_flask_csrf_token, mock_captcha_validation_error):
    """
    Description: check if user can login with captcha error
    """
    user_form = {
        "login": "louloute",
        "email": "louloute@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/login/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Echec vérification hCaptcha, essayez de nouveau" in html.unescape(
        response.get_data(as_text=True)
    )


def test_post_flask_register_route(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if we can register new user
    """
    user_form = {
        "login": "fafa",
        "email": "fafa@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}X",
        "password_check": f"{settings.TEST_USER_PWD}X",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Bienvenue fafa, avant de pouvoir vous connecter, utilisez le lien" in response.data


def test_post_flask_register_route_with_existing_email(client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if we can register new user with an already existing email
    """
    user_form = {
        "login": "leon",
        "email": "daisy@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Email existe d\xc3\xa9j\xc3\xa0 en base" in response.data


def test_post_flask_register_route_with_existing_email_and_unactivated_account(client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if we can register new user with an already existing email but account unactivated
    """
    user_form = {
        "login": "louloute",
        "email": "louloute@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Compte inactif, lien " in response.data


def test_post_flask_register_route_with_passwords_mismatch(
    client, get_flask_csrf_token, mock_captcha_validation
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
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mots de passe ne correspondent pas" in response.data


def test_post_flask_register_route_with_existing_user(client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if we can register new user with an already existing username
    """
    user_form = {
        "login": "donald",
        "email": "leon@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"Nom utilisateur existe d\xc3\xa9j\xc3\xa0, veuillez le modifier" in response.data


def test_post_flask_register_route_without_hcaptcha(client, get_flask_csrf_token):
    """
    Description: check if we can register new user without captcha validation
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    user_form = {
        "login": "donald",
        "email": "leon@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "",
    }
    response = client.post(
        "/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Veuillez valider le captcha" in response.text


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
        "http://localhost/register/", headers="", data=user_form
    )
    assert response.status_code == 400


def test_flask_register_with_captcha_error(app, client, get_flask_csrf_token, mock_captcha_validation_error):
    """
    Description: check if user can login with captcha error
    """
    user_form = {
        "login": "daddycool",
        "email": "daddycool@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}",
        "password_check": f"{settings.TEST_USER_PWD}",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Echec vérification hCaptcha, essayez de nouveau" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_register_with_too_simple_password_(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if user can register with password too simple
    """
    user_form = {
        "login": "daddy",
        "email": "daddy@localhost.fr",
        "password": "cool",
        "password_check": "cool",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Mot de passe trop simple, essayez de nouveau" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_register_with_existing_email(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if user can register when email already used
    """
    user_form = {
        "login": "daddy",
        "email": "donald@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Email existe déjà en base" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_register_with_unmatching_passwords(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if user can register when unmatching passwords
    """
    user_form = {
        "login": "daddy",
        "email": "daddycool@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": f'{settings.TEST_USER_PWD}X',
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Mots de passe ne correspondent pas" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_register_successfully(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if user can register successfully
    """
    user_form = {
        "login": "mummy",
        "email": "mummycool@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/register/",
        headers=headers,
        data=user_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Bienvenue mummy, avant de pouvoir vous connecter, utilisez le lien envoyé" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_login_with_valid_credentials(client, get_flask_csrf_token, mock_captcha_validation):
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
        "h-captcha-response": "dummy_response",
    }
    response = client.post(
        "/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Vous nous avez manq" in response.data


def test_flask_login_without_captcha_validation(client, get_flask_csrf_token):
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
        "h-captcha-response": "",
    }
    response = client.post(
        "/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Veuillez valider le captcha" in response.text


def test_flask_login_with_invalid_login(client, get_flask_csrf_token, mock_captcha_validation):
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
        "h-captcha-response": "dummy_response",
    }
    response = client.post(
        "/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Identifiants invalides" in response.data


def test_flask_login_with_invalid_email(client, get_flask_csrf_token, mock_captcha_validation):
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
        "h-captcha-response": "dummy_response",
    }
    response = client.post(
        "/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Identifiants invalides" in response.data


def test_flask_login_with_invalid_password(client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check the login with invalid password
    """
    headers = {
        "Content-Type": "multipart/form-data"
    }
    login_form = {
        "login": "daisy",
        "email": "daisy@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}X",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }
    response = client.post(
        "/login/",
        headers=headers,
        data=login_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Mot de passe ou email invalide." in response.data


def test_flask_get_logout(client, access_session):
    """
    Description: check if logout works.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("http://localhost/logout/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"plus connect" in response.data
