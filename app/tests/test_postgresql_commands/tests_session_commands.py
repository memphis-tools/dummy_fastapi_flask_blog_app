"""
All the tests functions dedicatd to test session_commands methods.
"""

from app.packages.database.commands import session_commands


def test_get_a_database_session():
    """test if we can get a session"""
    session = session_commands.get_a_database_session()
    assert session is not None
