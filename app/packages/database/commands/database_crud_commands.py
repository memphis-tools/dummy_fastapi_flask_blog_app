"""
CRUD commands for any SGBD, executed through the sqlalchemy.
"""

try:
    from app.packages.database.models import models
except ModuleNotFoundError:
    from packages.database.models import models


def commit_update(session):
    """commit_update -> commit any query and return True if success"""
    session.commit()
    return True


def add_instance(session, instance):
    """add an instance of a model"""
    session.add(instance)
    return commit_update(session)


def delete_instance(session, instance):
    """delete an instance of a model"""
    session.delete(instance)
    return commit_update(session)


def get_instance(session, instance, id):
    """get an instance of a model from an id"""
    instance_query = session.get(instance, id)
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
