"""
All the tests functions for the authentication from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
import pytest
from datetime import timedelta

import app.packages.settings as settings
from app.packages.fastapi.models import fastapi_models
from app.packages.fastapi.routes import routes_and_authentication


def test_register_uri(get_fastapi_client):
    """
    Description: test a get register url, method is not allowed.
    """
    response = get_fastapi_client.get("/api/v1/register/")
    assert response.status_code == 405


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


@pytest.mark.asyncio
async def test_register_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test register new user through FastAPI.
    """
    access_token = get_fastapi_token
    json = {
        "username": "tintin",
        "email": "tintin@localhost.fr",
        "password": f"{os.getenv('TEST_USER_PWD')}X",
        "password_check": f"{os.getenv('TEST_USER_PWD')}X",
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
async def test_register_with_invalid_username_data(
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
async def test_register_with_invalid_password_data(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test register new user through FastAPI with unmatching passwords.
    """
    access_token = get_fastapi_token
    json = {
        "username": "string",
        "email": "tintin@localhost.fr",
        "password": f"{os.getenv('TEST_USER_PWD')}xxx",
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
async def test_register_with_not_enough_complex_password_data(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test register new user through FastAPI with password not enough complex.
    """
    access_token = get_fastapi_token
    json = {
        "username": "string",
        "email": "tintin@localhost.fr",
        "password": settings.TEST_USER_PWD[:5],
        "password_check": settings.TEST_USER_PWD[:5],
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
    Description: test register new user through FastAPI with invalid datas.
    """
    access_token = get_fastapi_token
    json = {
        "username": "tintin",
        "email": "tintin@localhost.fr",
        "password": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 422


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
