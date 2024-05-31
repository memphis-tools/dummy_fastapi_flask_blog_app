"""
All the tests functions for the users passwords from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest

from app.packages import settings
from app.packages.fastapi.routes import routes_and_authentication
from app.packages.fastapi.routes.dependencies import verify_password


def test_get_password_hash():
    """
    Description: try to get a hash password from plain text.
    """
    password = settings.TEST_USER_PWD
    response = routes_and_authentication.get_password_hash(password)
    assert isinstance(response, str)


def test_verify_password_hash():
    """
    Description: check if password can be hashed.
    """
    plain_password = settings.TEST_USER_PWD
    hashed_password = routes_and_authentication.get_password_hash(plain_password)
    response = verify_password(plain_password, hashed_password)
    assert response is True


@pytest.mark.asyncio
async def test_update_user_password_being_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test update user password being admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": f"{settings.TEST_USER_PWD}123",
    }
    response = fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_password_with_wrong_method(fastapi_client, fastapi_token):
    """
    Description: test update user password with post method.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": f"{settings.TEST_USER_PWD}123",
    }
    response = fastapi_client.post(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_update_user_password_with_uncomplex_being_legitimate_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update user password through FastAPI with password not enough complex.
    """
    access_token = fastapi_token
    json = {
        "current_password": f"{settings.TEST_USER_PWD}123",
        "new_password": settings.TEST_USER_PWD[:5],
        "new_password_check": settings.TEST_USER_PWD[:5],
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.put("/api/v1/users/2/password/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Mot de passe trop simple, essayez de nouveau."}' in response.content


@pytest.mark.asyncio
async def test_update_user_password_being_legitimate_user(fastapi_client, fastapi_token):
    """
    Description: test update user password being the legitimate user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": f"{settings.TEST_USER_PWD}123",
        "new_password": f"{settings.TEST_USER_PWD}456",
        "new_password_check": f"{settings.TEST_USER_PWD}456",
    }
    response = fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_mismatched_password_being_legitimate_user(fastapi_client, fastapi_token):
    """
    Description: test update user mismatched password being the legitimate user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": f"{settings.TEST_USER_PWD}456",
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": f"{settings.TEST_USER_PWD}987",
    }
    response = fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_without_being_legitimate_user(fastapi_client, fastapi_token):
    """
    Description: test update user password without being the legitimate user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": f"{settings.TEST_USER_PWD}123",
    }
    response = fastapi_client.put(
        "/api/v1/users/1/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_password_with_blank_being_legitimate_user(fastapi_client, fastapi_token):
    """
    Description: test update user password with a blank string being the legitimate user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": "",
        "new_password_check": f"{settings.TEST_USER_PWD}123",
    }
    response = fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_check_with_blank_being_legitimate_user(fastapi_client, fastapi_token):
    """
    Description: test update user password with a blank string being the legitimate user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": "",
    }
    response = fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_with_wrong_current_password_being_legitimate_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update user password through FastAPI with wrong current password.
    """
    access_token = fastapi_token
    json = {
        "current_password": settings.TEST_USER_PWD[:5],
        "new_password": settings.TEST_USER_PWD,
        "new_password_check": settings.TEST_USER_PWD,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.put("/api/v1/users/2/password/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_unexisting_user_password(fastapi_client, fastapi_token):
    """
    Description: test update password for an unexisting user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": f"{settings.TEST_USER_PWD}123",
        "new_password_check": f"{settings.TEST_USER_PWD}123",
    }
    response = fastapi_client.put(
        "/api/v1/users/55555555/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 404
