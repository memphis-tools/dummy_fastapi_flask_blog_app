"""
All the tests functions for the models from FastAPI's uri /urls.
Notice that by default we already add dummies data through the application utils module.
"""

import pytest
from httpx import AsyncClient
try:
    from app.packages.fastapi.models import fastapi_models
    from app.packages.fastapi.routes import routes_and_authentication
    from app.packages.flask_app.project.__init__ import check_book_fields
except ModuleNotFoundError:
    from packages.fastapi.models import fastapi_models
    from packages.fastapi.routes import routes_and_authentication
    from packages.flask_app.project.__init__ import check_book_fields


app = routes_and_authentication.app


def test_docs_uri(get_fastapi_client):
    """
    Description: test a get docs url.
    """
    response = get_fastapi_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_views_without_authentication(get_fastapi_client):
    """
    Description: test view routes from FastAPI TestClient without token.
    """
    uris = ["users", "books", "comments"]
    for uri in uris:
        response = get_fastapi_client.get(f"/api/v1/{uri}")
        assert response.status_code == 401


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


def test_check_book_fields():
    """
    Description: test the check_book_fields function.
    """
    new_book = fastapi_models.NewBookModel(
        title="This is a dummy title sir",
        summary="This is a dummy summary sir",
        content="This is a dummy content sir",
        author="This is a dummy author sir",
        category="1",
        year_of_publication="1999",
        book_picture_name="dummy_filename.png",
        user_id=2,
    )
    response = check_book_fields(new_book)
    assert response is True


def test_check_book_fields_with_invalid_field():
    """
    Description: test the check_book_fields function.
    """
    new_book = fastapi_models.NewBookModel(
        title="This is a dummy title sir",
        author="This is a dummy author sir",
        summary="This is a dummy summary sir",
        content="string",
        category="1",
        year_of_publication="1999",
        book_picture_name="dummy_filename.png",
        user_id=2,
    )
    response = check_book_fields(new_book)
    assert "Saisie invalide, mot clef string non utilisable." == response
