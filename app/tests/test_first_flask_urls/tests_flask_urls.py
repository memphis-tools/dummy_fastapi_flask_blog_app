"""
All the tests functions for the flask urls.
Notice that by default we already add dummies data through the application utils module.
"""


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
    response = client.get("http://localhost", follow_redirects=True)
    assert response.status_code == 200


def test_flask_index_route(client):
    """
    Description: check if we can reach the index route
    """
    response = client.get("http://localhost/home/")
    assert response.status_code == 200
    assert b"DUMMY OPS" in response.data


def test_flask_ops_route(client, captured_templates):
    """
    Description: check if we can reach the ops route
    """
    response = client.get("/ops/")
    assert response.status_code == 200
    assert b'ops-portfolio' in response.data
    assert b'id="ops-hero"' in response.data
    assert captured_templates[0].name == "ops.html"


def test_flask_moocs_route(client):
    """
    Description: check if we can reach the moocs route
    """
    response = client.get("/moocs/")
    assert response.status_code == 200
    assert b'HAVE I BEEN PWNED' in response.data


def test_flask_contact_route(client):
    """
    Description: check if we can reach the contact route
    """
    response = client.get("http://localhost/contact/")
    assert response.status_code == 200
    assert b"DUMMY OPS - CONTACTEZ NOUS" in response.data


def test_flask_books_route(client):
    """
    Description: check if we can reach the books route
    """
    response = client.get("http://localhost/books/")
    assert response.status_code == 200
    assert b'class="post-title">Au commencement' in response.data


def test_flask_update_book_route(client):
    """
    Description: check if we can reach the update books route
    """
    response = client.get("http://localhost/book/1/update/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_update_comment_route(client):
    """
    Description: check if we can reach the update books route
    """
    response = client.get("http://localhost/comment/1/update/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_categories_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/books/categories/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_users_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/books/users/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_stats_route_as_admin(client, access_session_as_admin):
    """
    Description: check if we can reach the stats route
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get(
        "http://localhost/stats/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200


# ------------------------------------------------------------------
# Supplementary tests proposed by Vibe (powered by glm-5-latest-short)
# on 2026-09-29 — goal: raise project/__init__.py coverage from 77% to
# max. Covers: index with few books, contact hCaptcha failure,
# send_activation_link production and development branches.
# Unreachable dead branches (332, 555, 557, 560) are documented in the
# test docstrings, not covered.
# ------------------------------------------------------------------
from unittest.mock import MagicMock


def test_flask_index_route_with_less_than_three_books(client, monkeypatch):
    """
    Description: covers line 160 -> 163: index when there are fewer books
    than MAX_BOOKS_ON_INDEX_PAGE. The dummy DB always has more, so we
    patch the module constant instead of emptying the table.
    """
    import app.packages.flask_app.project as project

    monkeypatch.setattr(project, "MAX_BOOKS_ON_INDEX_PAGE", 99999)
    response = client.get("http://localhost/home/")
    assert response.status_code == 200
    assert b"DUMMY OPS" in response.data


def test_flask_contact_route_with_failing_captcha(
    client, mock_captcha_validation_error, get_flask_csrf_token
):
    """
    Description: covers line 202 -> 209: the hCaptcha verification fails,
    so the contact form is re-rendered with an error flash.
    """
    data = {
        "name": "John Doe",
        "email": "john.doe@localhost.fr",
        "message": "Hello there sir",
        "csrf_token": get_flask_csrf_token,
        "h-captcha-response": "dummy_response",
    }
    response = client.post(
        "http://localhost/contact/", data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Echec v\xc3\xa9rification hCaptcha" in response.data


def test_send_activation_link_in_production(app, monkeypatch):
    """
    Description: covers line 420 -> 421: in production the activation
    email is sent through SendGrid. get_secret is patched and
    SendGridAPIClient.send is mocked so no real secret/network is used.
    """
    import app.packages.flask_app.project as project

    monkeypatch.setenv("SCOPE", "production")
    monkeypatch.setattr(project, "get_secret", lambda path: "dummy-secret")
    monkeypatch.setattr(
        "sendgrid.SendGridAPIClient.send", lambda self, message: None
    )
    with app.test_request_context("/"):
        # url_for(..., _external=True) needs a request context
        project.send_activation_link("someone@localhost.fr")


def test_send_activation_link_in_development(app, monkeypatch):
    """
    Description: covers line 439 -> 441: in development the activation
    email is sent through MailTrap SMTP. smtplib.SMTP is mocked so no
    network access happens.
    """
    import app.packages.flask_app.project as project

    mock_smtp = MagicMock()
    monkeypatch.setattr("smtplib.SMTP", mock_smtp)
    monkeypatch.setenv("SCOPE", "development")
    with app.test_request_context("/"):
        project.send_activation_link("someone@localhost.fr")
    assert mock_smtp.called is True
    mock_smtp.return_value.__enter__.assert_called_once()
