"""
All the tests functions for the user model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest
from httpx import AsyncClient
from datetime import timedelta

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
    response = get_fastapi_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {access_token}"})
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
            "/api/v1/users/", headers={"Authorization": f"Bearer {get_fastapi_token}"}
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
        "password": settings.TEST_USER_PWD,
        "password_check": settings.TEST_USER_PWD,
    }
    response = get_fastapi_client.post(
        "/api/v1/users/",
        headers=headers,
        json=json
    )
    assert response.status_code == 200


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
    assert response.status_code == 204


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
            "/api/v1/users/", headers={"Authorization": "Bearer somethingWeird"}
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
async def test_update_user_with_authentication_with_invalid_datas(get_fastapi_client, get_fastapi_token):
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
async def test_update_user_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
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
    access_token = get_fastapi_token_for_admin
    response = get_fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_existing_email(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Email existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_existing_username(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Nom utilisateur daisylady existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_forbidden_role(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Affecter role admin autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_unexisting_role(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 404
    assert b'{"detail":"Role inconnu."}' in response.content


@pytest.mark.asyncio
async def test_update_unexisting_user_with_authentication(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/55555555/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_with_authentication_with_disabling_true(get_fastapi_client, get_fastapi_token):
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"D\xc3\xa9sactiver utilisateur autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_update_user_with_authentication_being_unlegetimate_user(
    get_fastapi_client,
    get_fastapi_token
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
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401
    assert b'{"detail":"Seul l\'utilisateur ou l\'admin peuvent mettre \xc3\xa0 jour l\'utilisateur"}' in response.content


@pytest.mark.asyncio
async def test_partial_update_forbidden_user_with_authentication(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 3 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.patch(
        "/api/v1/users/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 2 with valid datas.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_existing_email(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 2 with already existing email.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Email utilisateur donald.duck@localhost.fr existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_username(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 2 with already existing username.
    """
    access_token = get_fastapi_token
    json = {"username": "donald"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Nom utilisateur donald existe d\xc3\xa9j\xc3\xa0."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_forbidden_role(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 2 with forbidden role.
    """
    access_token = get_fastapi_token
    json = {"role": "admin"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 401
    assert b'{"detail":"Affecter role admin autoris\xc3\xa9 aux seuls admins."}' in response.content


@pytest.mark.asyncio
async def test_partial_update_user_with_authentication_with_unexisting_role(get_fastapi_client, get_fastapi_token):
    """
    Description: test partial update_user id 2 with unexisting role route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"role": "bucheron"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/2/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_partial_update_unexisting_user_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test partial update_user id 55555555 route with FastAPI TestClient with token.
    User does not exist.
    """
    access_token = get_fastapi_token
    json = {"email": "donald.duck@localhost.fr"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.patch("/api/v1/users/55555555/", headers=headers, json=json)
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
            f"/api/v1/users/{user_id}/books/",
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
            f"/api/v1/users/{user_id}/books/",
            headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 404


# @pytest.mark.asyncio
# async def test_update_user_password_being_admin(get_fastapi_client, get_fastapi_token_for_admin):
#     """
#     Description: test update user password being admin.
#     """
#     access_token = get_fastapi_token_for_admin
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }
#     json = {
#         "current_password": settings.TEST_USER_PWD,
#         "new_password": f"{settings.TEST_USER_PWD}123",
#         "new_password_check": f"{settings.TEST_USER_PWD}123",
#     }
#     response = get_fastapi_client.put(
#         "/api/v1/users/2/password/",
#         headers=headers,
#         json=json
#     )
#     assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_password_with_wrong_method(get_fastapi_client, get_fastapi_token):
    """
    Description: test update user password with post method.
    """
    access_token = get_fastapi_token
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
    response = get_fastapi_client.post(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 405


# @pytest.mark.asyncio
# async def test_update_user_password_being_legitimate_user(get_fastapi_client, get_fastapi_token):
#     """
#     Description: test update user password being the legitimate user.
#     """
#     access_token = get_fastapi_token
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }
#     json = {
#         "current_password": f"{settings.TEST_USER_PWD}123",
#         "new_password": f"{settings.TEST_USER_PWD}456",
#         "new_password_check": f"{settings.TEST_USER_PWD}456",
#     }
#     response = get_fastapi_client.put(
#         "/api/v1/users/2/password/",
#         headers=headers,
#         json=json
#     )
#     assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_unexisting_user_password(get_fastapi_client, get_fastapi_token):
    """
    Description: test update password for an unexisting user.
    """
    access_token = get_fastapi_token
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
    response = get_fastapi_client.put(
        "/api/v1/users/55555555/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 404


# @pytest.mark.asyncio
# async def test_update_user_mismatched_password_being_legitimate_user(get_fastapi_client, get_fastapi_token):
#     """
#     Description: test update user mismatched password being the legitimate user.
#     """
#     access_token = get_fastapi_token
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }
#     json = {
#         "current_password": f"{settings.TEST_USER_PWD}456",
#         "new_password": f"{settings.TEST_USER_PWD}123",
#         "new_password_check": f"{settings.TEST_USER_PWD}987",
#     }
#     response = get_fastapi_client.put(
#         "/api/v1/users/2/password/",
#         headers=headers,
#         json=json
#     )
#     assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_without_being_legitimate_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update user password without being the legitimate user.
    """
    access_token = get_fastapi_token
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
    response = get_fastapi_client.put(
        "/api/v1/users/1/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_user_password_with_blank_being_legitimate_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update user password with a blank string being the legitimate user.
    """
    access_token = get_fastapi_token
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
    response = get_fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_check_with_blank_being_legitimate_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update user password with a blank string being the legitimate user.
    """
    access_token = get_fastapi_token
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
    response = get_fastapi_client.put(
        "/api/v1/users/2/password/",
        headers=headers,
        json=json
    )
    assert response.status_code == 406


@pytest.mark.asyncio
async def test_update_user_password_with_uncomplex_being_legitimate_user(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test update user password through FastAPI with password not enough complex.
    """
    access_token = get_fastapi_token
    json = {
        "current_password": settings.TEST_USER_PWD,
        "new_password": settings.TEST_USER_PWD[:5],
        "new_password_check": settings.TEST_USER_PWD[:5],
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.put("/api/v1/users/2/password/", headers=headers, json=json)
    assert response.status_code == 406


# @pytest.mark.asyncio
# async def test_update_user_password_with_wrong_current_password_being_legitimate_user(
#     get_fastapi_client,
#     get_fastapi_token
# ):
#     """
#     Description: test update user password through FastAPI with wrong current password.
#     """
#     access_token = get_fastapi_token
#     json = {
#         "current_password": settings.TEST_USER_PWD,
#         "new_password": settings.TEST_USER_PWD,
#         "new_password_check": settings.TEST_USER_PWD,
#     }
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }
#
#     response = get_fastapi_client.put("/api/v1/users/2/password/", headers=headers, json=json)
#     assert response.status_code == 401
