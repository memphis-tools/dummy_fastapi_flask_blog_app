"""
All the tests functions dedicatd to test init_database methods.
Notice that we create a dummy test database in order to make the tests. So there is few functions to check here.
"""

import os

from app.packages.database.models.models import BookCategory, User
from app.packages.database import init_database


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
    session = init_database.get_a_database_session()
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
    engine = init_database.get_engine(username, password, host, port, database_name)
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
    assert init_database.update_default_postgres_password(get_session) is True

# ------------------------------------------------------------------
# Supplementary tests proposed by Vibe (powered by glm-5-latest-short)
# on 2026-09-29 — goal: raise init_database.py coverage from 79% to max.
# Covers: get_engine database-creation branch, get_a_database_session
# production branch, and init_database production branch (with mocked
# engine/session so nothing real is touched).
# ------------------------------------------------------------------
from unittest.mock import MagicMock

from sqlalchemy_utils import database_exists, drop_database


def test_get_engine_creates_a_new_database():
    """
    Description: covers line 38 -> 39: the database does not exist yet,
    so it is created with all the tables. A disposable database is used
    and dropped at the end of the test.
    """
    username = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db_name = "vibe_dummy_test_database"
    url = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}"
    engine = None
    try:
        engine = init_database.get_engine(username, password, host, port, db_name)
        assert engine.name == "postgresql"
        assert database_exists(url) is True
    finally:
        # release pooled connections, otherwise DROP DATABASE fails
        # with ObjectInUse
        if engine is not None:
            engine.dispose()
        drop_database(url)
    assert database_exists(url) is False


def test_get_a_database_session_with_production_scope(monkeypatch):
    """
    Description: covers line 54 -> 55: with SCOPE=production the password
    is read from the docker secret. create_engine/sessionmaker are lazy,
    so no real connection is attempted with the dummy secret.
    """
    monkeypatch.setattr(init_database, "get_secret", lambda path: "dummy-secret")
    monkeypatch.setenv("POSTGRES_PRODUCTION_DB_NAME", "dummy_production_db")
    monkeypatch.setenv("SCOPE", "production")
    session = init_database.get_a_database_session()
    assert session.__class__.__name__ == "Session"
    session.close()


def test_init_database_with_production_scope(monkeypatch):
    """
    Description: covers lines 76 -> 77, 90 -> 97, 131 -> 132, 142 -> 154
    and 167 -> 168: the production branch of init_database. get_engine,
    sessionmaker and get_secret are mocked so no real database or secret
    is involved: admin/categories are checked against a mocked session.
    """
    fake_session = MagicMock()
    # admin exists (scalar not None) -> covers the "already exists" branch
    fake_session.query.return_value.filter_by.return_value.scalar.return_value = (
        object()
    )
    # no book category yet -> the creation loop runs on the mocked session
    fake_session.query.return_value.all.return_value = []
    fake_engine = MagicMock()
    monkeypatch.setattr(init_database, "get_engine", lambda *args: fake_engine)
    monkeypatch.setattr(
        init_database, "sessionmaker", lambda bind: (lambda: fake_session)
    )
    monkeypatch.setattr(init_database, "get_secret", lambda path: "dummy-secret")
    monkeypatch.setenv("SCOPE", "production")
    session = init_database.init_database()
    assert session is fake_session
