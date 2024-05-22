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


def test_flask_update_book_route(client):
    """
    Description: check if we can reach the update books route
    """
    response = client.get("http://localhost/front/book/1/update/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_update_comment_route(client):
    """
    Description: check if we can reach the update books route
    """
    response = client.get("http://localhost/front/comment/1/update/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/front/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_categories_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/front/books/categories/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_users_stats_route(client):
    """
    Description: check if we can reach the books categories route
    """
    response = client.get("http://localhost/front/books/users/stats/", follow_redirects=True)
    assert response.status_code == 200
    assert b'Vous devez d&#39;abord vous connecter' in response.data


def test_flask_stats_route(client, access_session_as_admin):
    """
    Description: check if we can reach the stats route
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get(
        "http://localhost/front/stats/", headers=headers, follow_redirects=True
    )
    assert response.status_code == 200
