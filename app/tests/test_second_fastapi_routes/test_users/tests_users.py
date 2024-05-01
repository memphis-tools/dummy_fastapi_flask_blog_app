"""
All the tests functions for the user model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
import pytest
from httpx import AsyncClient
from datetime import timedelta
from werkzeug.security import generate_password_hash

import app.packages.settings as settings
from app.packages.fastapi.models import fastapi_models
from app.packages.fastapi.routes import routes_and_authentication

app = routes_and_authentication.app


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
async def test_view_users_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_users route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/users", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_users(get_fastapi_token):
    """
    Description:
    Check if we can reach the users uri served by FastAPI with a valid authentication token.
    Check if we can get the dummy users created for tests purposes.
    Notice that the dummies datas (users, books, comments) are in the test database.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/users", headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_user_being_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test add user being admin.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "username": "georges",
        "email": "georges@localhost.fr",
        "password": f"{settings.TEST_USER_PWD}X",
        "password_check": f"{settings.TEST_USER_PWD}X",
    }
    response = get_fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_add_user_with_invalid_datas(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test add user without valid datas.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    json = {
        "username": "georges",
        "email": "georges@localhost.fr",
        "password": settings.TEST_USER_PWD,
    }
    response = get_fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_user_without_being_admin(get_fastapi_client, get_fastapi_token):
    """
    Description: test add user without being admin.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    json = {
        "username": "georges",
        "email": "georges@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
    }
    response = get_fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_without_being_admin(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete user id 3 whereas user is not admin.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_being_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test delete user id 5 being admin.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete(
        "/api/v1/users/5/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_delete_unexisting_user_being_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test delete unexisting user id 55555555 being admin.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete(
        "/api/v1/users/55555555/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_users_without_valid_token():
    """
    Description:
    Ensure that we can not reach the users uri served by FastAPI without a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/users", headers={"Authorization": "Bearer somethingWeird"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_user_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_user id 1 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get(
        "/api/v1/users/1/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
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
async def test_update_uneixsting_user_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_user id 55555555 route with FastAPI TestClient with token.
    User does not exist.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/users/55555555/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_user_without_authentication(get_fastapi_client):
    """
    Description: test view_user id 2 route with FastAPI TestClient without token.
    """
    response = get_fastapi_client.get(
        "/api/v1/users/2/",
        headers={"Authorization": "Bearer bebopalula"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_books(get_fastapi_token):
    """
    Description:
    Ensure that we can get any user book's diffusion.
    """
    user_id = 2
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            f"/api/v1/{user_id}/books/",
            headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_user_books(get_fastapi_token):
    """
    Description:
    Ensure that we can get any invalid user diffusion.
    """
    user_id = 2555
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            f"/api/v1/{user_id}/books/",
            headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 404
