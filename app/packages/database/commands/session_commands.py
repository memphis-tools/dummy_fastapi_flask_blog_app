""" Define functions dedicated to return a session from a postgresql engine"""

from app.packages.database import init_database

def init_and_get_a_database_session():
    """
    Description:
    Function initialize database and return a session to query it for the FastAPI app.
    """
    session = init_database.init_database()
    return session


def get_a_database_session():
    """
    Description:
    Function return a session to query it for the Flask app.
    This is also the function called when running tests.
    """
    session = init_database.get_a_database_session()
    return session
