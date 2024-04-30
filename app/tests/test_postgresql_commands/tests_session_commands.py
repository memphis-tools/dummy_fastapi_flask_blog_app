"""
All the tests functions dedicatd to test session_commands methods.
"""

import pytest
try:
    from app.packages.database.commands import session_commands
except ModuleNotFoundError:
    from packages.database.commands import session_commands


def test_get_a_database_session():
    """test if we can get a session"""
    session = session_commands.get_a_database_session("postgresql")
    assert session is not None


def test_get_a_database_session_fot_unset_sgbd():
    """test if we can get a session for an unset sgbd"""
    session = session_commands.get_a_database_session("mysql")
    assert session is None


def test_get_a_database_session_without_sgbd():
    """test if we can get a session without sgbd param"""
    with pytest.raises(TypeError) as exception:
        session = session_commands.get_a_database_session()
    assert str(exception.value) == "get_a_database_session() missing 1 required positional argument: 'engine_name'"


def test_init_and_get_a_database_session_without_sgbd():
    """test if we can init and get a database session without sgbd param"""
    with pytest.raises(TypeError) as exception:
        session = session_commands.init_and_get_a_database_session()
    assert str(exception.value) == "init_and_get_a_database_session() missing 1 required positional argument: 'engine_name'"
