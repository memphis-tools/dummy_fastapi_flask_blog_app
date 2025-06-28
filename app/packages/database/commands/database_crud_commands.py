"""
CRUD commands for any SGBD, executed through the sqlalchemy.
"""

try:
    from database.models import models
except ModuleNotFoundError:
    from app.packages.database.models import models


def commit_update(session):
    """commit_update -> commit any query and return True if success"""
    session.commit()
    return True


def is_user_role_valid(role):
    """
    Description: check if user role exists

    Parameters:
    role -- str, the expected user role
    """
    roles_list = [r.value for r in models.Role]
    if role not in roles_list:
        return False
    return True


def add_instance(session, instance):
    """add an instance of a model"""
    session.add(instance)
    return commit_update(session)


def delete_instance(session, instance):
    """delete an instance of a model"""
    session.delete(instance)
    return commit_update(session)


def get_instance(session, instance, instance_id):
    """get an instance of a model from an id"""
    instance_query = session.get(instance, instance_id)
    return instance_query


def view_all_instances(session, instance):
    """view all instances from a model"""
    instances = session.query(instance).all()
    instances_list = []
    for elem in instances:
        if instance == models.User:
            instances_list.append(elem.get_restricted_json())
        else:
            instances_list.append(elem.get_json())
    return instances_list


def view_all_user_books(session, user_id):
    """view all books from an user_id"""
    user_books_query = session.query(models.Book).filter(
        models.Book.user_id.in_(
            [
                user_id,
            ]
        )
    )
    user_books = user_books_query.all()
    user_books_list = []
    for instance in user_books:
        user_books_list.append(instance.get_json())
    return user_books_list


def view_all_user_comments(session, user_id):
    """view all books from an user_id"""
    user_comments_query = session.query(models.Comment).filter(
        models.Comment.author_id.in_(
            [
                user_id,
            ]
        )
    )
    user_comments = user_comments_query.all()
    user_comments_list = []
    for instance in user_comments:
        user_comments_list.append(instance.get_json())
    return user_comments_list


def view_all_categories_instances(session):
    """view all categories instances"""
    categories_query = session.query(models.BookCategory).order_by(models.BookCategory.title).all()
    categories_list = []
    for category in categories_query:
        total_category_books = (
            session.query(models.Book)
            .filter(
                models.Book.category.in_(
                    [
                        category.id,
                    ]
                )
            )
            .count()
        )
        categories_list.append(
            {
                "id": category.id,
                "name": category.title,
                "total_books": total_category_books,
            }
        )
    return categories_list


def view_all_category_books(session, category_id):
    """view all books from a category filter by category_id"""
    categories_query = session.query(models.Book).filter(
        models.Book.category.in_(
            [
                category_id,
            ]
        )
    )
    category_books = categories_query.all()
    return category_books
