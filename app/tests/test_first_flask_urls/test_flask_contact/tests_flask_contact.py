"""
All the tests functions for the flask contact.
"""


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
