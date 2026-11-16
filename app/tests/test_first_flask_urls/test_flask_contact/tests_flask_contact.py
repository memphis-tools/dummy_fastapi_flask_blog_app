"""
All the tests functions for the flask contact.
"""

from unittest.mock import MagicMock


def test_flask_contact_route(client):
    """
    Description: check if we can reach the contact route
    """
    response = client.get("http://localhost/contact/")
    assert response.status_code == 200
    assert b"DUMMY OPS - CONTACTEZ NOUS" in response.data


def test_post_flask_contact_route(app, client, get_flask_csrf_token, mock_captcha_validation):
    """
    Description: check if we can use the contact route
    """
    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/contact/",
        headers=headers,
        data=contact_form,
        follow_redirects=True,
    )
    assert b"Veuillez valider le captcha" in response.data
    assert response.status_code == 200


def test_contact_failure(app, client, get_flask_csrf_token, mock_captcha_validation_error):
    """
    Description: check if we can use the contact facility with an invalid captcha
    """
    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy-token"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = client.post(
        "http://localhost/contact/",
        headers=headers,
        data=contact_form,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Echec vérification hCaptcha".encode() in response.data



##
# 16/11/2016 - Ajout 4 tests identifiés par Mistral-ai
def test_post_flask_contact_route_with_valid_captcha(
    app, client, get_flask_csrf_token, mock_captcha_validation, monkeypatch
):
    """
    Description: covers lines 209-211 and branch 202 -> 209: with a valid
    captcha and SCOPE=test, the form datas are read after the hCaptcha
    verification. SCOPE is set explicitly so the ambient environment
    does not change the code path.
    """
    monkeypatch.setenv("SCOPE", "test")

    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    response = client.post(
        "http://localhost/contact/",
        data=contact_form,
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_post_flask_contact_route_in_production(
    app, client, get_flask_csrf_token, mock_captcha_validation, monkeypatch
):
    """
    Description: covers lines 213-231: in production the contact message is
    sent through SendGrid. get_secret and SendGridAPIClient.send are mocked
    so no real secret/network is used; we assert on the mock, not on the
    rendered template wording.
    """
    import app.packages.flask_app.project as project

    monkeypatch.setenv("SCOPE", "production")
    monkeypatch.setattr(project, "get_secret", lambda path: "dummy-secret")
    send_mock = MagicMock()
    monkeypatch.setattr("sendgrid.SendGridAPIClient.send", send_mock)

    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    response = client.post("http://localhost/contact/", data=contact_form)
    assert response.status_code == 200
    assert send_mock.call_count == 1


def test_post_flask_contact_route_in_production_with_sendgrid_failure(
    app, client, get_flask_csrf_token, mock_captcha_validation, monkeypatch
):
    """
    Description: covers lines 232-241: in production, when the SendGrid send
    fails, the error branch is executed and a page is rendered.
    """
    import app.packages.flask_app.project as project

    monkeypatch.setenv("SCOPE", "production")
    monkeypatch.setattr(project, "get_secret", lambda path: "dummy-secret")
    send_mock = MagicMock(side_effect=Exception("dummy sendgrid failure"))
    monkeypatch.setattr("sendgrid.SendGridAPIClient.send", send_mock)

    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    response = client.post("http://localhost/contact/", data=contact_form)
    assert response.status_code == 200
    assert send_mock.call_count == 1


def test_post_flask_contact_route_in_development(
    app, client, get_flask_csrf_token, mock_captcha_validation, monkeypatch
):
    """
    Description: covers lines 242-276: in development the contact message is
    sent through the MailTrap SMTP server. smtplib.SMTP is mocked so no
    network access happens; we assert on the mock calls, not on the
    redirect/render behaviour which may differ between environments.
    """
    mock_smtp = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", mock_smtp)
    monkeypatch.setenv("SCOPE", "development")

    contact_form = {
        "name": "fafa",
        "email": "fafa@localhost.fr",
        "message": "A dummy message sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }

    response = client.post("http://localhost/contact/", data=contact_form)
    assert response.status_code in (200, 302)
    assert mock_smtp.called is True
    smtp_instance = mock_smtp.return_value.__enter__.return_value
    smtp_instance.send_message.assert_called_once()