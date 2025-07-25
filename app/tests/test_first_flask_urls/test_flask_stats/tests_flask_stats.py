"""
All the tests functions for the stats urls.
Notice that by default we already add dummies data through the application utils module.
"""

from app.packages.flask_app.project.stat_routes_blueprint import (
    create_books_categories_chart,
    create_users_chart,
)


def test_create_books_categories_chart():
    """
    Description: ensure we a get a figure from create_books_categories_chart
    """
    total_books = 3
    categories_books_count_dict = {
        "histoire": 2,
        "francais": 1
    }
    fig = create_books_categories_chart(total_books, categories_books_count_dict)
    assert f"{fig}" == "Figure(900x600)"


def test_categories_stats(client, access_session):
    """
    Description: ensure we a get a stats pie chart from categories_stats route
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "/books/categories/stats/",
        headers=headers,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'DOCTYPE html' in response.data
    assert b'DUMMY OPS - LES CATEGORIES' in response.data


def test_create_users_chart():
    """
    Description: ensure we a get a figure from create_users_chart
    """
    total_books = 3
    users_books_count_dict = {
        "donald": 2,
        "daisy": 1
    }
    fig = create_users_chart(total_books, users_books_count_dict)
    assert f"{fig}" == "Figure(900x600)"


def test_users_stats(client, access_session):
    """
    Description: ensure we a get a stats pie chart from users_stats route
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    response = client.get(
        "/books/users/stats/",
        headers=headers,
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'DOCTYPE html' in response.data
    assert b'DUMMY OPS - LES UTILISATEURS' in response.data
