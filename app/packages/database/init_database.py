""" some usefull functions used to initialise the database """

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy_utils import create_database, database_exists

try:
    import utils
    import settings
    from database.models import models
except ModuleNotFoundError:
    from app.packages import utils, settings
    from app.packages.database.models import models


def get_engine(
    username,
    password,
    host,
    port,
    db_name
):
    """
    Description: return a postgresql engine.

    Parameters:
    username -- str, name of super user on postgresql
    password -- str, password of super user on postgresql
    host -- str, host of postgresql
    port -- str, port of postgresql
    db_name -- str, name of database to work with on postgresql
    """
    url = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}"
    if not database_exists(url):
        print(f"[+] No existing database, we create one based on the {os.getenv('SCOPE')} scope sir.")
        create_database(url)
        engine = create_engine(url)
        models.BASE.metadata.create_all(engine)
        print(f"[+] Database and tables created for {os.getenv('SCOPE')} scope sir.")
    else:
        engine = create_engine(url)
        print(f"[+] Database exists for {os.getenv('SCOPE')} scope sir, nothing to do.")
    return engine


def get_a_database_session():
    """
    Description: return a postgresql engine's session.
    """
    if os.getenv("SCOPE") == "production":
        db_name = os.getenv("POSTGRES_PRODUCTION_DB_NAME")
        with open("/run/secrets/POSTGRES_PASSWORD", 'r') as f:
            password = f.read().strip()
    else:
        db_name = os.getenv("POSTGRES_TEST_DB_NAME")
        password = os.getenv("POSTGRES_PASSWORD")
    session = None

    username = os.getenv("POSTGRES_USER")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    url = f"postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(url)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def init_database():
    """
    Description: we get a session from a database.
    """
    if os.getenv("SCOPE") == "production":
        db_name = os.getenv("POSTGRES_PRODUCTION_DB_NAME")
        with open("/run/secrets/POSTGRES_PASSWORD", 'r') as f:
            password = f.read().strip()
    else:
        db_name = os.getenv("POSTGRES_TEST_DB_NAME")
        password = os.getenv("POSTGRES_PASSWORD")
    username = os.getenv("POSTGRES_USER")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database_name = db_name
    engine = get_engine(username, password, host, port, database_name)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    if os.getenv("SCOPE") == "test" or os.getenv("SCOPE") == "local_test":
        models.BASE.metadata.drop_all(engine)
        models.BASE.metadata.create_all(engine)
        create_application_admin_user_if_not_exist(session)
        create_books_categories_if_not_exist(session)
        reset_and_populate_database(session)
    else:
        create_application_admin_user_if_not_exist(session)
        create_books_categories_if_not_exist(session)
        update_default_postgres_password(session)
    print("[+] The database application is ready sir.")

    return session


def create_books_categories_if_not_exist(session):
    """
    Description: create all books categories declared in settings.
    """
    categories = session.query(models.BookCategory).all()
    if len(categories) == 0:
        for category in settings.BOOKS_CATEGORIES:
            book_category = models.BookCategory(
                title=category
            )
            session.add(book_category)
            session.commit()
        return True
    return '[+] Books categories already set sir, nothing to do.'


def create_application_admin_user_if_not_exist(session):
    """
    Description: create an application admin user.
    This is one which will allow to act as an admin on the Flask and the FasAPI apps.

    Parameters:
    session -- engine's session to query postgresql database
    """
    if os.getenv("SCOPE") == "production":
        with open("/run/secrets/ADMIN_LOGIN", 'r') as f:
            admin_login = f.read().strip()
        with open("/run/secrets/ADMIN_EMAIL", 'r') as f:
            admin_email = f.read().strip()
        with open("/run/secrets/ADMIN_PASSWORD", 'r') as f:
            admin_password = f.read().strip()
        admin = (
            session.query(models.User).filter_by(username=admin_login).scalar()
        )
        if admin is None:
            admin_user = models.User(
                username=admin_login,
                email=admin_email,
                hashed_password=utils.set_a_hash_password(admin_password),
                disabled=False,
                role=models.Role.R1,
            )
            session.add(admin_user)
            session.commit()
    else:
        admin = (
            session.query(models.User).filter_by(username=os.getenv("ADMIN_LOGIN")).scalar()
        )
        if admin is None:
            admin_user = models.User(
                username=os.getenv("ADMIN_LOGIN"),
                email=os.getenv("ADMIN_EMAIL"),
                hashed_password=utils.set_a_hash_password(os.getenv("ADMIN_PASSWORD")),
                disabled=False,
                role=models.Role.R1,
            )
            session.add(admin_user)
            session.commit()
        else:
            print(
                f'[+] Application {os.getenv("ADMIN_LOGIN")} account already exists sir, nothing to do.'
            )


def update_default_postgres_password(session):
    """
    Description: we update the postgres user password.

    Parameters:
    session -- engine's session to query postgresql database
    """
    if os.getenv("SCOPE") == "production":
        with open("/run/secrets/POSTGRES_PASSWORD", 'r') as f:
            updated_password = "'" + f.read().strip() + "'"
    else:
        updated_password = "'" + os.getenv("POSTGRES_PASSWORD") + "'"
    statement = f"ALTER USER {os.getenv('POSTGRES_USER')} WITH PASSWORD {updated_password};"
    session.execute(text(statement))
    print(f'[+] Default {os.getenv("POSTGRES_USER")} password updated sir.')
    return True


def reset_and_populate_database(session):
    """
    Description:
    The function resets database datas, and populates it with dummy ones if client ask for.
    It is called by init_database function which is called from session_commands.init_and_get_a_database_session.
    Each FastAPI and Flask apps call the "get_a_database_session".
    We don't need to execute the function twice, so we check if donald user exist (one of the dummy users).
    If the donald user exist that means the database is alread set up.
    To see all dummy datas created, see utils module.

    Parameters:
    session -- engine's session to query postgresql database
    """
    donald = (
        session.query(models.User).filter_by(username="donald").scalar()
    )
    if donald is None:
        utils.call_dummy_setup(session)
        print("[+] All previous dummy datas deleted and the default ones recreated.")
    return True
