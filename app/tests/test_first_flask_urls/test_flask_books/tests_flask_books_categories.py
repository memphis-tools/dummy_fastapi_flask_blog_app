"""
All the tests functions for the books categories urls.
Notice that by default we already add dummies data through the application utils module.
"""

from bs4 import BeautifulSoup

from app.packages.database.commands import session_commands
from app.packages.database.models.models import BookCategory
from app.packages.flask_app.project.__init__ import format_book_category
from app.packages.flask_app.project.book_category_routes_blueprint import check_book_category_fields


def test_check_book_category_fields_with_valid_datas():
    """
    Description: test the check_book_category_fields function.
    """
    new_category = BookCategory(
        title="Sophrologie"
    )
    response = check_book_category_fields(new_category)
    assert response is True


def test_check_book_category_fields_with_invalid_datas():
    """
    Description: test the check_book_category_fields function with invalid category.
    """
    new_category = BookCategory(
        title="string"
    )
    response = check_book_category_fields(new_category)
    assert "Saisie invalide, mot clef string non utilisable" in response


def test_check_book_category_fields_with_existing_category():
    """
    Description: test the check_book_category_fields function with already existing category.
    """
    new_category = BookCategory(
        title="politique"
    )
    response = check_book_category_fields(new_category)
    assert "Saisie invalide, categorie existe deja" in response


def test_get_books_categories(client, access_session):
    """
    Description: check if we can get all the books categories.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/books/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - LES LIVRES PAR CATEGORIES' in response.data


def test_get_books_categories_from_database_as_admin():
    """
    Description: check if we can request the database in order to get all quotes as admin.
    """
    session = session_commands.get_a_database_session()
    categories = session.query(BookCategory).all()
    session.close()
    assert len(categories) == 8


def test_get_valid_category_books(client, access_session):
    """
    Description: check if we can get all the books from a valid category.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/books/categories/1/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - LES LIVRES DE LA CATEGORIE' in response.data


def test_get_unexisting_category_books(client, access_session_as_admin):
    """
    Description: check if we can get all the books from an invalid category.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.get("/books/categories/55555/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'Categorie id 55555 inexistante' in response.data


def test_get_invalid_category_books(client, access_session_as_admin):
    """
    Description: check if we can get all the books from an invalid category.
    """
    url = "http://localhost/book/categories/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    data = {
        "title": "string",
        "csrf_token": csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post("/book/categories/add/", headers=headers, data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Saisie invalide, mot clef string non utilisable.' in response.data


def test_get_manage_books_categories_without_being_admin(client, access_session):
    """
    Description: check if we can get the mange books category without being admin.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 403


def test_get_manage_books_categories_being_admin(client, access_session_as_admin):
    """
    Description: check if we can get the manage books category being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.get("/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 200


def test_delete_valid_book_category_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can delete a valid book category withoutbeing admin.
    """
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "/book/categories/2/delete/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_delete_valid_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
    """
    Description: check if we can delete a valid book category being admin.
    """
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200


def test_delete_unexisting_book_category_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can delete an unexisting book category being admin.
    """
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/555555/delete/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    print(f"DEBUG SIR: {response.data}")
    assert response.status_code == 404


def test_update_valid_book_category_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can update a valid book category without being admin.
    """
    data = {
        "title": "something",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "/book/categories/2/update/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_update_valid_book_category_being_admin(client, access_session_as_admin):
    """
    Description: check if we can update a valid book category being admin.
    """
    url = "http://localhost/book/categories/2/update/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    data = {
        "title": "electronique",
        "csrf_token": csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/2/update/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"[+] Flask - Mise \xc3\xa0 jour cat\xc3\xa9gorie livre." in response.data


def test_format_book_category():
    """
    Description: test the custom template filter format_book_category.
    """
    response = format_book_category(1)
    assert response.title == "politique"


def test_add_book_category_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can add an existing book category without being admin.
    """
    data = {
        "title": "POLITIQUE",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "/book/categories/add/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_add_book_category_being_admin(client, access_session_as_admin):
    """
    Description: check if we can add a book category being admin.
    """
    url = "http://localhost/book/categories/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    data = {
        "title": "CUISINE",
        "csrf_token": csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/add/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Ajout cat\xc3\xa9gorie cuisine' in response.data


def test_add_existing_book_category_being_admin(client, access_session_as_admin):
    """
    Description: check if we can add an existing book category being admin.
    """
    url = "/book/categories/add/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    data = {
        "title": "POLITIQUE",
        "csrf_token": csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/add/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Saisie invalide, categorie existe deja' in response.data


def test_update_unexisting_book_category_being_admin(
    client,
    access_session_as_admin,
    get_flask_csrf_token
):
    """
    Description: check if we can update an unexisting book category being admin.
    """
    data = {
        "title": "something",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "/book/categories/55555/update/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 404
