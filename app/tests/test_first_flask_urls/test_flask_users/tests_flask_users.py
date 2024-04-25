"""
All the tests functions for the users urls.
Notice that by default we already add dummies data through the application utils module.
"""

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
    Try with dummy user id 5555.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/user/5555/books/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'Utilisateur id 5555 inexistant' in response.data


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
