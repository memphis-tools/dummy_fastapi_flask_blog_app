"""
All the tests functions for the books model from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest
from app.packages.database.models.models import Book
from app.packages.flask_app.project.book_routes_blueprint import check_book_fields


@pytest.mark.asyncio
async def test_view_books_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_books route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/books/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_book_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_book id 1 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/books/1/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_view_book_without_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_book id 1 route with FastAPI TestClient with token.
    """
    response = get_fastapi_client.get("/api/v1/books/1/", headers={"Authorization": "Bearer bebopalula"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_unexisting_book_being_authenticated(get_fastapi_client, get_fastapi_token):
    """
    Description: test view_book id 55555 route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    response = get_fastapi_client.get("/api/v1/books/55555/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 3 route with FastAPI TestClient with token.
    """
    json = {"summary": "such a book"}
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/books/3/",
        headers={"Authorization": f"Bearer {access_token}"},
        data=json
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 2 route with FastAPI TestClient with token.
    The book has not been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/books/2/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_unexisting_book_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 55555 route with FastAPI TestClient with token.
    The book does not exists.
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    access_token = get_fastapi_token
    response = get_fastapi_client.put(
        "/api/v1/books/55555/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test update_book id 1 route with FastAPI TestClient with token.
    The book has been published by authenticated user.
    """
    access_token = get_fastapi_token
    json = {
        "summary": "such a book",
        "year_of_publication": "2013",
        "category": "politique"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/1/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_book_with_authentication_with_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "2013",
        "category": "politique"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_book_fields(get_fastapi_client):
    """
    Description: test check_book_fields when adding a new book
    """
    book = Book(
        title="Perdus dans les Andes",
        author="Carl Barks",
        summary="Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        content="what a great story sir",
        book_picture_name="dummy_photo_name.jpg",
        year_of_publication="bebopalula",
        category="art"
    )
    response = check_book_fields(book)
    assert "Saisie invalide, annee publication livre doit etre un entier" in response


@pytest.mark.asyncio
async def test_post_book_without_authentication(get_fastapi_client):
    """
    Description: test add book without being authenticated
    """
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "2013",
        "category": "art"
    }
    headers = {
        "Authorization": "Bearer dummyToken",
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_datas(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    We must supply all attributes in order to post a book.
    """
    access_token = get_fastapi_token
    json = {"summary": "such a book", "other_id": "1"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_book_category(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    Category "supplication" does not exist so FastAPI will return a 422 error.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "2013",
        "category": "supplication"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_book_with_authentication_without_valid_publication_year(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, without valid datas.
    Publication year is relative to the publication year (in real world, not published on the app).
    A String will return a 422 error.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "Carl Barks",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "bebopalula",
        "category": "supplication"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_book_with_authentication_with_invalid_keyword_string(get_fastapi_client, get_fastapi_token):
    """
    Description: test add book route with FastAPI TestClient with token, with the invalid keyword string.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "StRing",
        "summary": "Donald a trouvé un emploi au musée : il doit dépoussiérer la collection de pierres.",
        "content": "what a great story sir",
        "book_picture_name": "dummy_photo_name.jpg",
        "year_of_publication": "1984",
        "category": "art"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.post("/api/v1/books/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_put_book_with_authentication_with_invalid_keyword_string(get_fastapi_client, get_fastapi_token):
    """
    Description: test put book route with FastAPI TestClient with token, with the invalid keyword string.
    """
    access_token = get_fastapi_token
    json = {
        "title": "Perdus dans les Andes",
        "author": "StRing",
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = get_fastapi_client.put("/api/v1/books/1/", headers=headers, json=json)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_with_authentication_with_forbidden_user(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_book id 2 route with FastAPI TestClient with token.
    Notice we try to delete a book that authenticated user has not published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/2/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_book_with_authentication(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_book id 1 route with FastAPI TestClient with token.
    Notice we try to delete a book that authenticated user has published
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/1/", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_book_without_authentication(get_fastapi_client,):
    """
    Description: test delete_book id 1 route without being authenticated
    """
    headers = {
        "Authorization": "Bearer dummyToken",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/1/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_unexisting_book(get_fastapi_client, get_fastapi_token):
    """
    Description: test delete_book id 55555 route with FastAPI TestClient with token.
    Notice we try to delete an unexisting book
    """
    access_token = get_fastapi_token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "accept": "application/json"
    }
    response = get_fastapi_client.delete("/api/v1/books/55555/", headers=headers)
    assert response.status_code == 404
