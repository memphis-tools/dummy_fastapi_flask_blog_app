"""
All the tests functions for the authentication from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
from datetime import timedelta
import pytest

from app.packages import settings
from app.packages.fastapi.models import fastapi_models
from app.packages.fastapi.routes import routes_and_authentication
from app.packages.fastapi.routes.dependencies import authenticate_user, get_user


def test_register_uri(fastapi_client):
    """
    Description: test a get register url, method is not allowed.
    """
    response = fastapi_client.get("/api/v1/register/")
    assert response.status_code == 405


def test_create_access_token():
    """
    Description: check if we can create an access token.
    """
    username = "donald"
    user = get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    assert isinstance(access_token, str)


@pytest.mark.asyncio
async def test_register_with_valid_datas(fastapi_client, fastapi_token):
    """
    Description: test register new user through FastAPI.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_with_valid_datas_for_already_existing_username(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI whereas username already exists.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_with_valid_datas_for_already_existing_email(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI whereas email already exists.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_with_invalid_username_data(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI with invalid datad.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_with_invalid_password_data(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI with unmatching passwords.
    """
    access_token = fastapi_token
    json = {
        "username": "tintinou",
        "email": "tintinou@localhost.fr",
        "password": f"{os.getenv('TEST_USER_PWD')}xxx",
        "password_check": os.getenv("TEST_USER_PWD"),
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_with_not_enough_complex_password_data(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI with password not enough complex.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_with_invalid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test register new user through FastAPI with invalid datas.
    """
    access_token = fastapi_token
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

    response = fastapi_client.post("/api/v1/register/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_token_for_enabled_user(fastapi_client):
    """
    Description: test a get token for enabled user.
    """
    form_data = dict(
        username="donald",
        password=settings.TEST_USER_PWD
    )
    response = fastapi_client.post("/api/v1/token/", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_get_token_for_unexisting_user(fastapi_client):
    """
    Description: test a get token for unexisting user.
    """
    form_data = dict(
        username="donaldxyz",
        password=settings.TEST_USER_PWD
    )
    response = fastapi_client.post("/api/v1/token/", data=form_data, follow_redirects=True)
    assert response.status_code == 401


def test_authenticate_user_with_good_credentials():
    """
    Description: check if we can authenticate an existing user.
    """
    username = "donald"
    password = settings.TEST_USER_PWD
    response = authenticate_user(username, password)
    assert isinstance(response, fastapi_models.UserInDB)


def test_authenticate_user_with_bad_credentials():
    """
    Description: check if we can not authenticate with bad credentials.
    """
    username = settings.TEST_USER_USERNAME
    password = settings.TEST_USER_PWD
    response = authenticate_user(username, password)
    assert response is False


def test_authenticate_unexisting_user():
    """
    Description: check if we can not authenticate an existing user.
    """
    username = "milou"
    password = settings.TEST_USER_PWD
    response = authenticate_user(username, password)
    assert response is False


# ------------------------------------------------------------------
# Supplementary tests proposed by Vibe (powered by glm-5-latest-short)
# on 2026-09-29 — goal: raise dependencies.py coverage from 84% to 100%.
# Covers: SCOPE branch, token without "sub", unknown user in token,
# disabled user, invalid JWT, and get_current_* happy paths.
# ------------------------------------------------------------------
import importlib
from datetime import timedelta  # already imported above; kept for block autonomy
import pytest  # already imported above

from fastapi import HTTPException

from app.packages.fastapi.routes import dependencies
from app.packages.fastapi.routes.dependencies import get_current_user, get_current_active_user


def _make_token(data):
    """helper: craft a signed token with an arbitrary payload."""
    return routes_and_authentication.create_access_token(
        data=data,
        expires_delta=timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@pytest.mark.asyncio
async def test_get_current_user_with_valid_token():
    """covers get_current_user happy path."""
    token = _make_token({"sub": "donald"})
    user = await get_current_user(token)
    assert isinstance(user, fastapi_models.UserInDB)
    assert user.username == "donald"


@pytest.mark.asyncio
async def test_get_current_active_user_with_valid_token():
    """covers get_current_active_user happy path (line 89 -> return)."""
    token = _make_token({"sub": "donald"})
    current_user = await get_current_active_user(await get_current_user(token))
    assert current_user.username == "donald"


@pytest.mark.asyncio
async def test_get_current_active_user_with_disabled_user():
    """covers line 89 -> 90: disabled user raises HTTP 400.
    Notice: User.get_json() omits "disabled", so UserInDB always gets
    disabled=False from get_user(); the branch is only reachable by
    calling get_current_active_user directly with a disabled UserModel.
    """
    disabled_user = fastapi_models.UserModel(
        id=4, username="louloute", role="user", disabled=True, is_active=True
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(disabled_user)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_current_user_with_token_without_sub_claim(fastapi_client):
    """covers line 74 -> 75: valid token but no 'sub' claim."""
    headers = {"Authorization": f"Bearer {_make_token({'foo': 'bar'})}"}
    response = fastapi_client.get("/api/v1/books/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_unknown_user_in_token(fastapi_client):
    """covers line 80 -> 81: valid token, user not in db."""
    headers = {"Authorization": f"Bearer {_make_token({'sub': 'fantomas'})}"}
    response = fastapi_client.get("/api/v1/books/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_with_garbage_token(fastapi_client):
    """covers the except branch of jwt.decode."""
    headers = {"Authorization": "Bearer not.a.valid.jwt"}
    response = fastapi_client.get("/api/v1/books/", headers=headers)
    assert response.status_code == 401


def test_secret_key_loaded_from_docker_secret(monkeypatch):
    """covers line 34 -> 35: SECRET_KEY read from /run/secrets when SCOPE is set.
    We patch the session factory so the module reload reuses the existing
    session instead of opening a new (failing) DB connection.
    """
    monkeypatch.setattr("app.packages.utils.get_secret", lambda path: "dummy-secret")
    monkeypatch.setattr(
        "app.packages.database.commands.session_commands.init_and_get_a_database_session",
        lambda: dependencies.session,
    )
    monkeypatch.setenv("SCOPE", "development")
    try:
        importlib.reload(dependencies)
        assert dependencies.SECRET_KEY == "dummy-secret"
    finally:
        monkeypatch.delenv("SCOPE", raising=False)
        importlib.reload(dependencies)
