"""
All the tests functions dedicatd to test init_database methods.
Notice that we create a dummy test database in order to make the tests. So there is few functions to check here.
"""

import os
try:
    from app.packages.database.models.models import BookCategory, User
    from app.packages.database import init_database
except ModuleNotFoundError:
    from packages.database.models.models import BookCategory, User
    from packages.database import init_database


def test_create_books_categories_if_not_exist(get_session):
    """
    Description: test book categories creation.
    """
    categories = get_session.query(BookCategory).all()
    assert len(categories) > 0


def test_create_books_categories_if_not_exist_through_package(get_session):
    """
    Description: test book categories creation through package.
    """
    response = init_database.create_books_categories_if_not_exist(get_session)
    assert "Books categories already set sir" in response


def test_create_application_admin_user_if_not_exist(get_session):
    """
    Description: test admin user creation.
    """
    admin = (
        get_session.query(User).filter_by(username=os.getenv("ADMIN_LOGIN")).scalar()
    )
    assert bool(admin) is True


def test_get_a_database_session():
    """
    Description: test get a database session.
    """
    session = init_database.get_a_database_session("postgresql")
    assert session.__class__.__name__ == "Session"


def test_get_engine():
    """
    Description: test get an engine.
    """
    db_name = os.getenv("POSTGRES_TEST_DB_NAME")
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database_name = db_name
    engine = init_database.get_engine("postgresql", username, password, host, port, database_name)
    assert engine.name == "postgresql"


def test_reset_and_populate_database(get_session):
    """
    Description: test the reset and populate database.
    """
    assert init_database.reset_and_populate_database(get_session) is True


def test_update_default_postgres_password(get_session):
    """
    Description: test the update password for postgres default user .
    """
    assert init_database.update_default_postgres_password("postgresql", get_session) is True
