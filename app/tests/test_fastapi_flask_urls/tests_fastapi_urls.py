"""
Notice that by default we already add dummies data through the application utils module.
We do it only in "test, dev" scope.
Application is served through Docker for the production scope. No test database here.
"""

import pytest
from httpx import AsyncClient

try:
    from app.packages.fastapi.routes import routes_and_authentication
except ModuleNotFoundError:
    from packages.fastapi.routes import routes_and_authentication


app = routes_and_authentication.app


@pytest.mark.asyncio
async def test_read_main(get_fastapi_client, get_fastapi_token):
    """
    Description:
    Check if we can reach the books uri served by FastAPI with a valid authentication token.
    Check if we can get the dummy books created for tests purposes.
    Notice that the dummies datas (users, books, comments) are in the test database.
    """
    response = get_fastapi_client.get(
        "/api/v1/books", headers={"Authorization": f"Bearer {get_fastapi_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 8


@pytest.mark.asyncio
async def test_read_main_without_valid_token():
    """
    Description:
    Ensure that we can not reach the books uri served by FastAPI without a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books", headers={"Authorization": "Bearer somethingWeird"}
        )
    assert response.status_code == 401


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
    assert len(response.json()) == 5


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
    assert len(response.json()) == 7


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
