"""
All the tests functions for the user model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

from datetime import timedelta
import pytest
# from fastapi import HTTPException
from app.packages import settings
from app.packages.fastapi.models import fastapi_models
from app.packages.fastapi.routes import routes_and_authentication
from app.packages.fastapi.routes.dependencies import get_user, get_current_user, get_current_active_user


def test_get_existing_user():
    """
    Description: check if we can get an user based on his username.
    """
    username = "donald"
    response = get_user(username)
    assert isinstance(response, fastapi_models.UserInDB)


def test_get_unexisting_user():
    """
    Description: check if we can get an unexisting user.
    """
    username = settings.TEST_USER_USERNAME
    response = get_user(username)
    assert response is None


@pytest.mark.asyncio
async def test_get_current_user():
    """
    Description: check if we can find user based on token.
    """
    username = "donald"
    user = get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await get_current_user(access_token)
    assert user_found.username == "donald"


@pytest.mark.asyncio
async def test_get_current_active_user():
    """
    Description: check if we can get current user if active.
    """
    username = "donald"
    user = get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await get_current_user(access_token)
    active_user = await get_current_active_user(user_found)
    assert isinstance(active_user, fastapi_models.UserInDB)


@pytest.mark.asyncio
async def test_get_current_disabled_user():
    """
    Description: check if we can get current user if disabled.
    """
    username = "louloute"
    user = get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_found = await get_current_user(access_token)
    assert isinstance(user, fastapi_models.UserInDB)
    active_user = await get_current_active_user(user)


@pytest.mark.asyncio
async def test_view_users_with_authentication(fastapi_client, fastapi_token):
    """
    Description: test view_users route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    response = fastapi_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_users(fastapi_client, fastapi_token):
    """
    Description:
    Check if we can reach the users uri served by FastAPI with a valid authentication token.
    Check if we can get the dummy users created for tests purposes.
    Notice that the dummies datas (users, books, comments) are in the test database.
    """
    response = fastapi_client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_user_being_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test add user being admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    json = {
        "username": "georges",
        "email": "georges@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
    }
    response = fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_user_with_invalid_datas(fastapi_client, fastapi_token_for_admin):
    """
    Description: test add user without valid datas.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    json = {
        "username": "georges",
        "email": "georges@localhost.fr",
        "password": settings.TEST_USER_PWD,
    }
    response = fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_user_without_being_admin(fastapi_client, fastapi_token):
    """
    Description: test add user without being admin.
    """
    access_token = fastapi_token
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
    response = fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_without_being_admin(fastapi_client, fastapi_token):
    """
    Description: test delete user id 3 whereas user is not admin.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = fastapi_client.delete(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_being_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test delete user id 5 being admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = fastapi_client.delete(
        "/api/v1/users/5/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_unexisting_user_being_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test delete unexisting user id 55555555 being admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = fastapi_client.delete(
        "/api/v1/users/55555555/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_users_without_valid_token(fastapi_client):
    """
    Description:
    Ensure that we can not reach the users uri served by FastAPI without a valid authentication token.
    """
    response = fastapi_client.get(
        "/api/v1/users/", headers={"Authorization": "Bearer somethingWeird"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_user_with_authentication(fastapi_client, fastapi_token):
    """
    Description: test view_user id 1 route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    response = fastapi_client.get(
        "/api/v1/users/1/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_invalid_datas(fastapi_client, fastapi_token):
    """
    Description: test update_user id 3 route with FastAPI TestClient with token.
    """
    json = {"email": "donald.duck@localhost.fr"}
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        data=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test update_user id 3 being authenticated as admin.
    """
    json = {
        "username": "daisylady",
        "email": "daisy.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "user",
        "disabled": False
    }
    access_token = fastapi_token_for_admin
    response = fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_existing_email(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 2 with forbidden role as legitimate user.
    """
    json = {
        "username": "donaldinox",
        "email": "donald@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "user"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Email existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_existing_username(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 2 with existing username.
    """
    json = {
        "username": "daisylady",
        "email": "donald.ducky@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "user"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Nom utilisateur daisylady existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_forbidden_role(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 2 with forbidden role as legitimate user.
    """
    json = {
        "username": "donaldinou",
        "email": "d.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "admin"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Affecter role admin autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_unexisting_role(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 2 with unexisting role as legitimate user.
    """
    json = {
        "username": "donaldinou",
        "email": "d.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "bucheron"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 404
    assert b'{"detail":"Role inconnu."}' in response.content


@pytest.mark.asyncio
async def test_update_unexisting_user_with_authentication(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 2 with unexisting role as legitimate user.
    """
    json = {
        "username": "donaldinou",
        "email": "d.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "bucheron"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/55555555/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_disabling_true(fastapi_client, fastapi_token):
    """
    Description: test update_user id 2 with unexisting role as legitimate user.
    """
    json = {
        "username": "donaldinou",
        "email": "d.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "user",
        "disabled": True
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"D\xc3\xa9sactiver utilisateur autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_being_unlegetimate_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update_user id 3 as unlegitimate user.
    """
    json = {
        "username": "daisy",
        "email": "daisy.duck@localhost.fr",
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
        "role": "user"
    }
    access_token = fastapi_token
    response = fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Seul l\'utilisateur ou l\'admin peuvent mettre \xc3\xa0 jour l\'utilisateur"}' in response.content


@pytest.mark.asyncio
async def test_partial_update_forbidden_user_with_authentication(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 3 route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = fastapi_token
    response = fastapi_client.patch(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 2 with valid datas.
    """
    access_token = fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_existing_email(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 2 with already existing email.
    """
    access_token = fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Email utilisateur donald.duck@localhost.fr existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_username(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 2 with already existing username.
    """
    access_token = fastapi_token
    json = {"username": "donald"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Nom utilisateur donald existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_forbidden_role(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 2 with forbidden role.
    """
    access_token = fastapi_token
    json = {"role": "admin"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Affecter role admin autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_unexisting_role(fastapi_client, fastapi_token):
    """
    Description: test partial update_user id 2 with unexisting role route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"role": "bucheron"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_partial_update_unexisting_user_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test partial update_user id 55555555 route with FastAPI TestClient with token.
    User does not exist.
    """
    access_token = fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.patch("/api/v1/users/55555555/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_user_without_authentication(fastapi_client):
    """
    Description: test view_user id 2 route with FastAPI TestClient without token.
    """
    response = fastapi_client.get(
        "/api/v1/users/2/",
        headers={"Authorization": "Bearer bebopalula"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_books(fastapi_client, fastapi_token):
    """
    Description:
    Ensure that we can get any user book's diffusion.
    """
    user_id = 2
    response = fastapi_client.get(
        f"/api/v1/users/{user_id}/books/",
        headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_user_books(fastapi_client, fastapi_token):
    """
    Description:
    Ensure that we can get any invalid user diffusion.
    """
    user_id = 2555
    response = fastapi_client.get(
        f"/api/v1/users/{user_id}/books/",
        headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 404
