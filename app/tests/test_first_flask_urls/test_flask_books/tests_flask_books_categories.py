"""
All the tests functions for the books categories urls.
Notice that by default we already add dummies data through the application utils module.
"""

try:
    from app.packages.database.models.models import BookCategory
    from app.packages.flask_app.project.__init__ import check_book_category_fields, format_book_category
    from app.packages import settings
except ModuleNotFoundError:
    from packages.database.models.models import BookCategory
    from packages.flask_app.project.__init__ import check_book_category_fields, format_book_category
    from packages import settings


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
    response = client.get("/front/books/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - LES LIVRES PAR CATEGORIES' in response.data


def test_get_valid_category_books(client, access_session):
    """
    Description: check if we can get all the books from a valid category.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/books/categories/1/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'DUMMY BLOG - LES LIVRES DE LA CATEGORIE' in response.data


def test_get_invalid_category_books(client, access_session):
    """
    Description: check if we can get all the books from a valid category.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/books/categories/55555/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b'Categorie id 55555 inexistante.' in response.data


def test_get_manage_books_categories_without_being_admin(client, access_session):
    """
    Description: check if we can get the mange books category without being admin.
    """
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.get("/front/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 403


def test_get_manage_books_categories_being_admin(client, access_session_as_admin):
    """
    Description: check if we can get the manage books category being admin.
    """
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.get("/front/categories/", headers=headers, follow_redirects=True)
    assert response.status_code == 200


def test_delete_valid_book_category_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can delete a valid book category withoutbeing admin.
    """
    data = {
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "http://localhost/front/book/categories/2/delete/",
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
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "http://localhost/front/book/categories/4/delete/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200


# def test_delete_invalid_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can delete an invalid book category being admin.
#     """
#     data = {
#         "csrf_token": get_flask_csrf_token,
#     }
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     response = client.post(
#         "/front/book/categories/555555/delete/",
#         headers=headers,
#         data=data,
#         follow_redirects=True
#     )
#     assert response.status_code == 404


def test_update_valid_book_category_without_being_admin(client, access_session, get_flask_csrf_token):
    """
    Description: check if we can update a valid book category without being admin.
    """
    data = {
        "title": "something",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "http://localhost/front/book/categories/2/update/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_update_valid_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
    """
    Description: check if we can update a valid book category being admin.
    """
    data = {
        "title": "politique",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "http://localhost/front/book/categories/3/update/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200


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
        "Cookie": f"session={access_session}"
    }
    response = client.post(
        "http://localhost/front/book/categories/add/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 403


def test_add_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
    """
    Description: check if we can add a book category being admin.
    """
    data = {
        "title": "CUISINE",
        "csrf_token": get_flask_csrf_token,
    }
    headers = {
        "Cookie": f"session={access_session_as_admin}"
    }
    response = client.post(
        "http://localhost/front/book/categories/add/",
        headers=headers,
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200


# def test_add_existing_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can add an existing book category being admin.
#     """
#     data = {
#         "title": "POLITIQUE",
#         "csrf_token": get_flask_csrf_token,
#     }
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     response = client.post(
#         "http://localhost/front/book/categories/add/",
#         headers=headers,
#         data=data,
#         follow_redirects=True
#     )
#     assert response.status_code == 200
#     assert b'Saisie invalide, categorie existe deja' in response.data


# def test_update_invalid_book_category_being_admin(client, access_session_as_admin, get_flask_csrf_token):
#     """
#     Description: check if we can update an invalid book category being admin.
#     """
#     data = {
#         "name": "something",
#         "csrf_token": get_flask_csrf_token,
#     }
#     headers = {
#         "Cookie": f"session={access_session_as_admin}"
#     }
#     response = client.post(
#         "/front/book/categories/55555/update/",
#         headers=headers,
#         data=data,
#         follow_redirects=True
#     )
#     assert response.status_code == 404
