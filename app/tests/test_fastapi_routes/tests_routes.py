"""
All the tests functions for the models from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
import pytest
from datetime import timedelta
try:
    import app.packages.settings as settings
    from app.packages.fastapi.models import fastapi_models
    from app.packages.fastapi.routes import routes_and_authentication
except ModuleNotFoundError:
    import packages.settings as settings
    from packages.fastapi.models import fastapi_models
    from packages.fastapi.routes import routes_and_authentication


def test_get_existing_user():
    """
    Description: check if we can get an user based on his username.
    """
    username = "donald"
    response = routes_and_authentication.get_user(username)
    assert type(response) is fastapi_models.UserInDB


def test_get_unexisting_user():
    """
    Description: check if we can get an unexisting user.
    """
    username = settings.TEST_USER_USERNAME
    response = routes_and_authentication.get_user(username)
    assert response is None


def test_get_password_hash():
    """
    Description: try to get a hash password from plain text.
    """
    password = settings.TEST_USER_PWD
    response = routes_and_authentication.get_password_hash(password)
    assert type(response) is str


def test_verify_password_hash():
    """
    Description: check if password can be hashed.
    """
    plain_password = settings.TEST_USER_PWD
    hashed_password = routes_and_authentication.get_password_hash(plain_password)
    response = routes_and_authentication.verify_password(plain_password, hashed_password)
    assert response is True


def test_create_access_token():
    """
    Description: check if we can create an access token.
    """
    username = "donald"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    assert type(access_token) is str


def test_docs_uri(get_fastapi_client):
    """
    Description: test a get docs url.
    """
    response = get_fastapi_client.get("/docs")
    assert response.status_code == 200


def test_register_uri(get_fastapi_client):
    """
    Description: test a get register url, method is not allowed.
    """
    response = get_fastapi_client.get("/api/v1/register/")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_register_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test register new user through FastAPI.
    """
    access_token = get_fastapi_token
    json = {
        "username": "tintin",
        "email": "tintin@localhost.fr",
        "password": os.getenv("TEST_USER_PWD"),
        "password_check": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_with_valid_datas_for_already_existing_username(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test register new user through FastAPI whereas username already exists.
    """
    access_token = get_fastapi_token
    json = {
        "username": "tintin",
        "email": "tintin@localhost.fr",
        "password": os.getenv("TEST_USER_PWD"),
        "password_check": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_with_valid_datas_for_already_existing_email(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test register new user through FastAPI whereas email already exists.
    """
    access_token = get_fastapi_token
    json = {
        "username": "lustucru",
        "email": "tintin@localhost.fr",
        "password": os.getenv("TEST_USER_PWD"),
        "password_check": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_with_invalid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test register new user through FastAPI with invalid datad.
    """
    access_token = get_fastapi_token
    json = {
        "username": "string",
        "email": "tintin@localhost.fr",
        "password": os.getenv("TEST_USER_PWD"),
        "password_check": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_without_being_admin(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete user id 2 whereas user is not admin.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/users/3/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user():
    """
    Description: check if we can find user based on token.
    """
    username = "donald"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await routes_and_authentication.get_current_user(access_token)
    assert user_found.username == "donald"


@pytest.mark.asyncio
async def test_get_current_active_user():
    """
    Description: check if we can get current user if active.
    """
    username = "donald"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await routes_and_authentication.get_current_user(access_token)
    active_user = await routes_and_authentication.get_current_active_user(user_found)
    assert type(active_user) is fastapi_models.UserInDB


@pytest.mark.asyncio
async def test_get_current_disabled_user():
    """
    Description: check if we can get current user if disabled.
    """
    username = "louloute"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await routes_and_authentication.get_current_user(access_token)
    active_user = await routes_and_authentication.get_current_active_user(user)
    assert type(active_user) is fastapi_models.UserInDB


@pytest.mark.asyncio
async def test_get_token_for_enabled_user(get_fastapi_client):
    """
    Description: test a get token for enabled user.
    """
    form_data = dict(
        username="donald",
        password=settings.TEST_USER_PWD
    )
    response = get_fastapi_client.post("/token", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_get_token_for_unexisting_user(get_fastapi_client):
    """
    Description: test a get token for unexisting user.
    """
    form_data = dict(
        username="donaldxyz",
        password=settings.TEST_USER_PWD
    )
    response = get_fastapi_client.post("/token", data=form_data, follow_redirects=True)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_views_without_authentication(get_fastapi_client):
    """
    Description: test view routes from FastAPI TestClient without token.
    """
    uris = ["users", "books", "comments"]
    for uri in uris:
        response = get_fastapi_client.get(f"/api/v1/{uri}")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_users_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_users route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/users", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_user_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_user id 1 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/users/1/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_user id 3 route with FastAPI TestClient with token.
    """
    json = {"email": "donald.duck@localhost.fr"}
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        data=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_forbidden_user_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_user id 3 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_user id 2 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_user_without_authentication(get_fastapi_client):
    """
    Description: test view_user id 2 route with FastAPI TestClient without token.
    """
    response = get_fastapi_client.get("/api/v1/users/2/", headers={"Authorization": "Bearer bebopalula"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_books_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_books route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/books", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_book_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_book id 1 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/books/1/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_book_without_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_book id 1 route with FastAPI TestClient with token.
    """
    response = get_fastapi_client.get("/api/v1/books/1/", headers={"Authorization": "Bearer bebopalula"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_book_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 3 route with FastAPI TestClient with token.
    """
    json = {"summary": "such a book"}
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/books/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        data=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 2 route with FastAPI TestClient with token.
    The book has not been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/books/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_book_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 1 route with FastAPI TestClient with token.
    The book has been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {
        "summary": "such a book",
        "year_of_publication": "2013",
        "category": "art"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/1/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_book_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "2013",
        "category": "art"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    We must supply all attributes in order to post a book.
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book", "other_id": "1"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_book_category(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    Category "supplication" does not exist so FastAPI will return a 422 error.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "2013",
        "category": "supplication"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_publication_year(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    Publication year is relative to the publication year (in real world, not published on the app).
    A String will return a 422 error.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "bebopalula",
        "category": "supplication"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_book_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_books id 2 route with FastAPI TestClient with token.
    Notice we try to delete a book that authenticated user has not published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/2/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_books id 1 route with FastAPI TestClient with token.
    Notice we try to delete a book that authenticated user has published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/1/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_view_comments_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_comments route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/comments", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_comment_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_comments id 1 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/comments/1/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_comment_without_authentication(get_fastapi_client):
    """
    Description: test view_comment id 1 route with FastAPI TestClient without token.
    """
    response = get_fastapi_client.get("/api/v1/comments/1/", headers={"Authorization": "Bearer bebopalula"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_comment_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_comment id 3 route with FastAPI TestClient with token.
    """
    json = {"text": "such a comment"}
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/comments/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        data=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_comment_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_comment id 1 route with FastAPI TestClient with token.
    The comment has not been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {"text": "such a comment"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/comments/6/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_comment_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_comment id 5 route with FastAPI TestClient with token.
    The comment has been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {"text": "such a comment"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/comments/5/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_comment_with_auth_with_valid_datas_for_unexisting_comment(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test update_comment id 2 route with FastAPI TestClient with token.
    The comment does not exist (no more)
    """
    access_token = get_fastapi_token
    json = {"text": "such a comment"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/comments/2/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_comment_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add comment to book id 2 route with FastAPI TestClient with token.
    Notice we have set a token for user id 2 ("donald")
    """
    access_token = get_fastapi_token
    json = {"text": "such a great book sir"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/comments/?book_id=2", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_comment_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add comment to book id 1 route with FastAPI TestClient with token.
    Notice we have set a token for user id 2 ("donald")
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book", "other_id": "1"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/comments/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_comment_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_comments id 6 route with FastAPI TestClient with token.
    Notice we try to delete a comment that authenticated user has not published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }

    response = get_fastapi_client.delete(
        "/api/v1/books/6/comments/6/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_comment_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_comments id 6 route with FastAPI TestClient with token.
    Notice we try to delete a comment that authenticated user has published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete(
        "/api/v1/books/6/comments/7/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


def test_authenticate_user_with_good_credentials():
    """
    Description: check if we can authenticate an existing user.
    """
    username = "donald"
    password = settings.TEST_USER_PWD
    response = routes_and_authentication.authenticate_user(username, password)
    assert type(response) is fastapi_models.UserInDB


def test_authenticate_user_with_bad_credentials():
    """
    Description: check if we can not authenticate with bad credentials.
    """
    username = settings.TEST_USER_USERNAME
    password = settings.TEST_USER_PWD
    response = routes_and_authentication.authenticate_user(username, password)
    assert response is False


def test_authenticate_unexisting_user():
    """
    Description: check if we can not authenticate an existing user.
    """
    username = "milou"
    password = settings.TEST_USER_PWD
    response = routes_and_authentication.authenticate_user(username, password)
    assert response is False
