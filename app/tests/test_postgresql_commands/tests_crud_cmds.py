"""
All the tests functions dedicatd to test sgbd crud commands.
Notice that by default we already add dummies data through the application utils module.
"""

from sqlalchemy import and_

from app.packages import settings
from app.packages import utils
from app.packages.database.commands import database_crud_commands
from app.packages.database.models import models


def test_commit_update(get_session):
    """ Description: test commit_update"""
    session = get_session
    query = database_crud_commands.commit_update(session)
    assert query is True


def test_add_user_instance(get_session):
    """ Description: test if we can add an user instance"""
    session = get_session
    instance = models.User(
        username="fifi",
        email="fifi@localhost.fr",
        hashed_password=utils.set_a_hash_password(settings.TEST_USER_PWD),
        role="user",
        disabled=False,
    )
    query = database_crud_commands.add_instance(session, instance)
    assert query is True


def test_get_user_instance(get_session):
    """ Description: test if we can get an user instance"""
    session = get_session
    instance = session.query(models.User).filter_by(username="fifi").scalar()
    assert isinstance(instance, models.User)
    # notice that the __str__ method from user instance returns the username
    assert str(instance).lower() == "fifi"


def test_delete_user_instance(get_session):
    """ Description: test if we can delete an user instance"""
    session = get_session
    instance = session.query(models.User).filter_by(username="fifi").scalar()
    query = database_crud_commands.delete_instance(session, instance)
    assert query is True


def test_get_instance(get_session):
    """ Description: test get_instance"""
    session = get_session
    instance = models.User
    id = 2
    instance = database_crud_commands.get_instance(session, instance, id)
    assert isinstance(instance, models.User)
    assert instance.username == "donald"


def test_view_all_user_instances(get_session):
    """ Description: test get all user instances"""
    session = get_session
    instance = models.User
    instances = database_crud_commands.view_all_instances(session, instance)
    assert isinstance(instances, list)


def test_view_all_book_instances(get_session):
    """ Description: test get all book instances"""
    session = get_session
    instance = models.Book
    instances = database_crud_commands.view_all_instances(session, instance)
    assert isinstance(instances, list)


def test_view_all_book_category__instances(get_session):
    """ Description: test get all book categories instances"""
    session = get_session
    instance = models.BookCategory
    instances = database_crud_commands.view_all_instances(session, instance)
    assert isinstance(instances, list)


def test_view_all_book_comment_instances(get_session):
    """ Description: test get all book comments instances"""
    session = get_session
    instance = models.Comment
    instances = database_crud_commands.view_all_instances(session, instance)
    assert isinstance(instances, list)


def test_add_book_instance(get_session):
    """ Description: test if we can add a book instance"""
    session = get_session
    instance = models.Book(
        title="This is a dummy test title sir",
        summary="This is a dummy summary sir",
        content="This is a dummy content sir",
        author="Dummy Sapiens",
        book_picture_name="dummy_book_image.jpg",
        user_id=2,
    )
    query = database_crud_commands.add_instance(session, instance)
    assert query is True


def test_get_book_instance(get_session):
    """ Description: test if we can get a book instance"""
    session = get_session
    instance = session.query(models.Book).filter_by(title="This is a dummy test title sir").scalar()
    assert isinstance(instance, models.Book)
    # notice that the __str__ method from book instance returns the title
    assert str(instance) == "This is a dummy test title sir"


def test_delete_book_instance(get_session):
    """ Description: test if we can delete a book instance"""
    session = get_session
    instance = session.query(models.Book).filter_by(title="This is a dummy test title sir").scalar()
    query = database_crud_commands.delete_instance(session, instance)
    assert query is True


def test_add_comment_instance(get_session):
    """ Description: test if we can add a comment instance"""
    session = get_session
    instance = models.Comment(
        text="Dummy comment sir",
        author_id=2,
        book_id=4,
    )
    query = database_crud_commands.add_instance(session, instance)
    assert query is True


def test_get_comment_instance(get_session):
    """ Description: test if we can get a comment instance"""
    session = get_session
    instance = session.query(models.Comment).filter(
        and_(
            models.Comment.author_id == 2,
            models.Comment.book_id == 4,
            models.Comment.text == "Dummy comment sir",
        )
    ).scalar()
    assert isinstance(instance, models.Comment)


def test_delete_comment_instance(get_session):
    """ Description: test if we can delete an user instance"""
    session = get_session
    instance = session.query(models.Comment).filter_by(text="Dummy comment sir").scalar()
    query = database_crud_commands.delete_instance(session, instance)
    assert query is True


def test_get_view_all_user_books(get_session):
    """ Description: test if we can get all books from a calid user """
    session = get_session
    books = session.query(models.Book).filter_by(user_id=2).all()
    assert len(books) > 0


def test_get_view_all_categories_instances(get_session):
    """ Description: test if we can get all books categories """
    session = get_session
    categories = session.query(models.BookCategory).all()
    assert len(categories) > 0


def test_get_view_all_category_books(get_session):
    """ Description: test if we can get all books from a category """
    session = get_session
    total_books = session.query(models.Book).filter(models.Book.category == 3).count()
    assert total_books >= 0
