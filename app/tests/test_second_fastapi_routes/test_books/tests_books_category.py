"""
All the tests functions for the books category  model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest
from httpx import AsyncClient
try:
    import app.packages.settings as settings
    from app.packages.fastapi.routes import routes_and_authentication
except ModuleNotFoundError:
    import packages.settings as settings
    from packages.fastapi.routes import routes_and_authentication


app = routes_and_authentication.app


@pytest.mark.asyncio
async def test_get_category_books(get_fastapi_token):
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/1/", headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_category_books_without_authentication():
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/1/",
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_category_books(get_fastapi_token):
    """
    Description:
    Check if we can reach an invalid category books.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/55555/",
            headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_category_books_as_admin(get_fastapi_token_for_admin):
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with admin token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/1/",
            headers={"Authorization": f"Bearer {get_fastapi_token_for_admin}"}
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_category_books_as_admin(get_fastapi_token_for_admin):
    """
    Description:
    Check if we can reach an invalid category books with admin token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/55555/",
            headers={"Authorization": f"Bearer {get_fastapi_token_for_admin}"}
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_books_categories_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_categories(get_fastapi_token):
    """
    Description:
    Check if we can reach the view_books_categories uri served by FastAPI with a valid authentication token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.get(
            "/api/v1/books/categories/",
            headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_category_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_category_without_authentication(get_fastapi_client):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_unexisting_books_category_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test get unexisting book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/55555/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test add book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"title": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_book_category_without_authentication_with_valid_datas(
    get_fastapi_client,
):
    """
    Description: test add book category route without being authenticated.
    """
    json = {"title": "mathematique"}
    headers = {
        "Authorization": f"Bearer dummyToken",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_with_invalid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test add book category route with invalid data and FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"category_name": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_existing_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test add existing book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"title": "roman"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test delete book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.delete("/api/v1/books/categories/5/delete/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_unexisting_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test delete unexisting book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.delete("/api/v1/books/categories/55555/delete/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test update book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/categories/1/update/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_unexisting_book_category_with_authentication_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token
):
    """
    Description: test update an unexisting book category route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/categories/55555/update/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_books_categories_with_authentication_as_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test get book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_book_category_with_authentication_as_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test get book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_unexisting_book_category_with_authentication_as_admin(get_fastapi_client, get_fastapi_token_for_admin):
    """
    Description: test get unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.get("/api/v1/books/categories/55555/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test add book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    json = {"title": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_as_admin_with_invalid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test add book category route with invalid data and FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    json = {"category_name": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_existing_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test add existing book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    json = {"title": "POLITIQUE"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test delete book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.delete("/api/v1/books/categories/5/delete/", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_unexisting_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test delete unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.delete("/api/v1/books/categories/55555/delete/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test update book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/categories/1/update/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_unexisting_book_category_with_authentication_as_admin_with_valid_datas(
    get_fastapi_client,
    get_fastapi_token_for_admin
):
    """
    Description: test update an unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = get_fastapi_token_for_admin
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/categories/55555/update/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_books(get_fastapi_token):
    """
    Description:
    Check if we can delete a book category through FastAPI.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.delete(
            "/api/v1/books/categories/6/delete/", headers={"Authorization": f"Bearer {get_fastapi_token}"}
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_category_books_as_admin(get_fastapi_token_for_admin):
    """
    Description:
    Check if we can delete a book category through FastAPI with admin token.
    """
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response = await ac.delete(
            "/api/v1/books/categories/7/delete/", headers={"Authorization": f"Bearer {get_fastapi_token_for_admin}"}
        )
    assert response.status_code == 204


# @pytest.mark.asyncio
# async def test_get_books_categories_as_admin(get_fastapi_token_for_admin):
#     """
#     Description:
#     Check if we can reach the view_books_categories uri served by FastAPI with admin token.
#     """
#     async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
#         response = await ac.get(
#             "/api/v1/books/categories/", headers={"Authorization": f"Bearer {get_fastapi_token_for_admin}"}
#         )
#     assert response.status_code == 200
