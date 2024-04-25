"""
All the tests functions for the comment model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import os
import pytest
from httpx import AsyncClient
try:
    from app.packages.fastapi.routes import routes_and_authentication
except ModuleNotFoundError:
    from packages.fastapi.routes import routes_and_authentication


app = routes_and_authentication.app


@pytest.mark.asyncio
async def test_view_comments_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_comments route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/comments", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_comments(get_fastapi_token):
    """
    Description:
    Check if we can reach the comments uri served by FastAPI with a valid authentication token.
    Check if we can get the dummy comments created for tests purposes.
    Notice that the dummies datas (users, books, comments) are in the test database.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/comments", headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_view_comments_without_valid_token():
    """
    Description:
    Ensure that we can not reach the comments uri served by FastAPI without a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/comments", headers={"Authorization": "Bearer somethingWeird"}
        )
    assert response.status_code == 401


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
async def test_update_comment_without_authentication(get_fastapi_client):
    """
    Description: test update_comment id 5 route without being authenticated
    """
    json = {"text": "such a comment"}
    headers = {
        "Authorization": f"Bearer dummyToken",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/comments/5/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_comment_with_auth_with_valid_datas_for_unexisting_comment(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test update unexisting comment id 55555 route with FastAPI TestClient with token.
    The comment does not exist (no more)
    """
    access_token = get_fastapi_token
    json = {"text": "such a comment"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/comments/55555/", headers=headers, json=json)
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
async def test_post_comment_without_being_authenticated(get_fastapi_client, get_fastapi_token):
    """
    Description: test add comment to book id 2 without being authenticated.
    """
    access_token = get_fastapi_token
    json = {"text": "such a great book sir"}
    headers = {
        "Authorization": f"Bearer DummyToken",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/comments/?book_id=2", headers=headers, json=json)
    assert response.status_code == 401


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


@pytest.mark.asyncio
async def test_delete_comment_without_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_comments id 6 without being authenticated
    """
    headers = {
        "Authorization": f"Bearer dummyToken",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete(
        "/api/v1/books/6/comments/7/",
        headers=headers
    )
    assert response.status_code == 401
