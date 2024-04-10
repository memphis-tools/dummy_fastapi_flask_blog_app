""" Define functions dedicated to return a session from a postgresql engine"""

try:
    from app.packages.database import init_database
except ModuleNotFoundError:
    from packages.database import init_database


def init_and_get_a_database_session(engine_name):
    """
    Description:
    Function initialize database and return a session to query it for the FastAPI app.

    Parameters:
    engine_name: str, postgresql by default
    """
    session = init_database.init_database(engine_name)
    return session


def get_a_database_session(engine_name):
    """
    Description:
    Function return a session to query it for the Flask app.
    This is also the function called when running tests.

    Parameters:
    engine_name: str, postgresql by default
    """
    session = init_database.get_a_database_session(engine_name)
    return session
