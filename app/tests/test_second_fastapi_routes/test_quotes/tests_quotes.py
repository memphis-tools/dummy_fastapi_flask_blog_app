"""
All the tests functions for the quotes model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest


@pytest.mark.asyncio
async def test_get_quotes_without_authentication(
    fastapi_client,
):
    """
    Description: test get quotes through FastAPI without authentication.
    """
    headers = {
        "Authorization": "Bearer bebopalula",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.get("/api/v1/quotes/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_quotes_as_standard_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test get quotes through FastAPI as standard user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.get("/api/v1/quotes/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_quotes_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test get quotes through FastAPI as admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.get("/api/v1/quotes/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_a_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test get a specific quote through FastAPI as admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.get("/api/v1/quotes/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_a_quote_as_standard_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test get a specific quote through FastAPI as standard user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.get("/api/v1/quotes/1/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_quote_without_authentication(
    fastapi_client
):
    """
    Description: test add quote route with FastAPI TestClient without authentication.
    """
    json = {
        "author": "Bruce Lee",
        "book_title": "Be Water",
        "quote": "Be Water my friend"
    }
    headers = {
        "Authorization": "Bearer bebopalula",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/quotes/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_quote_as_standard_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test add quote route with FastAPI TestClient as standard user.
    """
    access_token = fastapi_token
    json = {
        "author": "Bruce Lee",
        "book_title": "Be Water",
        "quote": "Be Water my friend"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/quotes/", headers=headers, json=json)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add quote route with FastAPI TestClient as admin.
    """
    access_token = fastapi_token_for_admin
    json = {
        "author": "Bruce Lee",
        "book_title": "Be Water",
        "quote": "Be Water my friend"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/quotes/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_empty_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add quote route with FastAPI TestClient as admin.
    """
    access_token = fastapi_token_for_admin
    json = {
        "author": "",
        "book_title": "Be Water",
        "quote": "Be Water my friend"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/quotes/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_malformed_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add malformed quote route with FastAPI TestClient as admin.
    """
    access_token = fastapi_token_for_admin
    json = {
        "book_title": "Be Water",
        "quote": "Be Water my friend"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.post("/api/v1/quotes/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_quote_as_standard_user(
    fastapi_client,
    fastapi_token
):
    """
    Description: test delete quote route with FastAPI TestClient as standard user.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.delete("/api/v1/quotes/4/", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test delete quote route with FastAPI TestClient as admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.delete("/api/v1/quotes/2/", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_unexisting_quote_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test delete unexisting quote route with FastAPI TestClient as admin.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = fastapi_client.delete("/api/v1/quotes/55555/", headers=headers)
    assert response.status_code == 404
