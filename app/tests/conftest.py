""" all needed fixtures for the application tests """

from datetime import timedelta
import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from app.packages.fastapi.routes import routes_and_authentication
from app.packages.database.commands import session_commands
from app.packages.flask_app import project
from app.packages import settings


ACCESS_TOKEN_EXPIRE_MINUTES = 3


@pytest.fixture
def get_session():
    """
    Description: fixture offers a postgresql engine's session.
    """
    session = session_commands.get_a_database_session()
    return session


@pytest.fixture
def fastapi_client(get_session):
    """
    Description: fixture offers a Flask TestClient
    """
    with TestClient(routes_and_authentication.app) as client:
        yield client


@pytest.fixture
def fastapi_token():
    """
    Description: fixture offers a FastAPI user's token.
    """
    username = "donald"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def fastapi_token_for_admin():
    """
    Description: fixture offers a FastAPI user's token.
    """
    username = "admin"
    user = routes_and_authentication.get_user(username)
    access_token_expires = timedelta(minutes=routes_and_authentication.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = routes_and_authentication.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def get_test_token():
    """
    Description: we need a token created from the app (and his secret key).
    We test a dummy user created in a test database.
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = routes_and_authentication.create_access_token(
        data={"sub": "donald"}, expires_delta=access_token_expires
    )
    return token


@pytest.fixture
def app():
    """
    Description: Provides the project Flask app for tests to run.
    """
    flask_app = project.app
    flask_app.config.update(
        {"TESTING": True, "WTF_CSRF_ENABLED": True, "LOGIN_DISABLED": False, "DEBUG": True}
    )
    yield flask_app


@pytest.fixture
def client(app):
    """
    Description: Provides a client of the project Flask app for tests to run.
    """
    with app.test_client() as client:
        yield client


@pytest.fixture
def get_flask_csrf_token(client):
    """
    Description: Provides a csrf_token from Flask app for tests to run.
    """
    url = "http://localhost/register/"
    soup = BeautifulSoup(client.get(url).text, 'html.parser')
    token = soup.find('input', {'name': 'csrf_token'})['value']
    return token


@pytest.fixture
def access_session(client, get_flask_csrf_token):
    """
    Description: fixture offers a Flask session cookie for a standard user.
    """
    data = {
        "login": "donald",
        "password": settings.TEST_USER_PWD,
        "email": "donald@localhost.fr",
        "csrf_token": get_flask_csrf_token
    }
    response = client.post("http://localhost/login/", data=data)
    session = response.headers.pop('Set-Cookie')
    return session


@pytest.fixture
def access_session_as_admin(client, get_flask_csrf_token):
    """
    Description: Provides a Flask session cookie for the admin user.
    """
    data = {
        "login": "admin",
        "password": settings.TEST_USER_PWD,
        "email": "admin@localhost.fr",
        "csrf_token": get_flask_csrf_token
    }
    response = client.post("http://localhost/login/", data=data)
    session = response.headers.pop('Set-Cookie')
    yield session


@pytest.fixture
def mock_function_delete_book(mocker):
    """
    Description: we mock the delete_book function.
    We do not want to really remove the book's illustration file (image).
    """
    mocker.patch("app.packages.flask_app.project.book_routes_blueprint.delete_book", return_value=True)
    mocker.patch("os.remove")
