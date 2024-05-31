"""
All the tests functions for the books category  model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest

from app.packages.database.models.models import BookCategory
from app.packages.flask_app.project.book_category_routes_blueprint import check_book_category_fields


@pytest.mark.asyncio
async def test_get_category_books(fastapi_client, fastapi_token):
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with a valid authentication token.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/1/", headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_book_category_fields():
    """
    Description: test check_book_category_fields when adding a new book category
    """
    book = BookCategory(
        title="string",
    )
    response = check_book_category_fields(book)
    assert "Saisie invalide, mot clef string non utilisable" in response


@pytest.mark.asyncio
async def test_get_category_books_without_authentication(fastapi_client):
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with a valid authentication token.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/1/",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_invalid_category_books(fastapi_client, fastapi_token):
    """
    Description:
    Check if we can reach an invalid category books.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/55555555/",
        headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_category_books_as_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description:
    Check if we can reach the view_category_books uri served by FastAPI with admin token.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/1/",
        headers={"Authorization": f"Bearer {fastapi_token_for_admin}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_invalid_category_books_as_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description:
    Check if we can reach an invalid category books with admin token.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/55555555/",
        headers={"Authorization": f"Bearer {fastapi_token_for_admin}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_books_categories_with_authentication(fastapi_client, fastapi_token):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_categories(fastapi_client, fastapi_token):
    """
    Description:
    Check if we can reach the view_books_categories uri served by FastAPI with a valid authentication token.
    """
    response = fastapi_client.get(
        "/api/v1/books/categories/",
        headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_category_with_authentication(fastapi_client, fastapi_token):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_books_category_without_authentication(fastapi_client):
    """
    Description: test get book category route with FastAPI TestClient with token.
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_unexisting_books_category_with_authentication(fastapi_client, fastapi_token):
    """
    Description: test get unexisting book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/55555555/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test add book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"title": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_book_category_without_authentication_with_valid_datas(
    fastapi_client,
):
    """
    Description: test add book category route without being authenticated.
    """
    json = {"title": "mathematique"}
    headers = {
        "Authorization": "Bearer dummyToken",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_with_invalid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test add book category route with invalid data and FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"category_name": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_existing_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test add existing book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"title": "roman"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test delete book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.delete("/api/v1/books/categories/5/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_unexisting_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test delete unexisting book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.delete("/api/v1/books/categories/55555555/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.put("/api/v1/books/categories/1/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_unexisting_book_category_with_authentication_with_valid_datas(
    fastapi_client,
    fastapi_token
):
    """
    Description: test update an unexisting book category route with FastAPI TestClient with token.
    """
    access_token = fastapi_token
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.put("/api/v1/books/categories/55555555/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_books_categories_with_authentication_as_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test get book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_book_category_with_authentication_as_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description: test get book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/1/", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_unexisting_book_category_with_authentication_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test get unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/55555555/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    json = {"title": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_book_category_with_authentication_as_admin_with_invalid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add book category route with invalid data and FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    json = {"category_name": "mathematique"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_existing_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test add existing book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    json = {"title": "POLITIQUE"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.post("/api/v1/books/categories/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test delete book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.delete("/api/v1/books/categories/5/", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_unexisting_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test delete unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.delete("/api/v1/books/categories/55555555/", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test update book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.put("/api/v1/books/categories/1/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_unexisting_book_category_with_authentication_as_admin_with_valid_datas(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description: test update an unexisting book category route with FastAPI TestClient with admin token.
    """
    access_token = fastapi_token_for_admin
    json = {"title": "politiques"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.put("/api/v1/books/categories/55555555/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_books(fastapi_client, fastapi_token):
    """
    Description:
    Check if we can delete a book category through FastAPI.
    """
    response = fastapi_client.delete(
        "/api/v1/books/categories/6/", headers={"Authorization": f"Bearer {fastapi_token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_category_books_as_admin(fastapi_client, fastapi_token_for_admin):
    """
    Description:
    Check if we can delete a book category through FastAPI with admin token.
    """
    response = fastapi_client.delete(
        "/api/v1/books/categories/7/", headers={"Authorization": f"Bearer {fastapi_token_for_admin}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_books_categories_as_admin(
    fastapi_client,
    fastapi_token_for_admin
):
    """
    Description:
    Check if we can reach the view_books_categories uri served by FastAPI with admin token.
    """
    access_token = fastapi_token_for_admin
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = fastapi_client.get("/api/v1/books/categories/", headers=headers)
    assert response.status_code == 200
