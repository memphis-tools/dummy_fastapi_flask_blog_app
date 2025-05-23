""" All the methods needed to be call from different blueprints """


import random
from functools import wraps
from flask import abort, request
from flask_login import current_user

try:
    import settings
    from database.commands import session_commands
    from database.models.models import Quote
except ModuleNotFoundError:
    from app.packages import settings
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Quote


def admin_only(f):
    """
    Description: allow a decorator to limit uri's access for admin only.
    """

    @wraps(f)
    def decorated_function(*args, **kw):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kw)

    return decorated_function


def return_pagination(items_to_paginate):
    """
    Description: manual pagination since we do not use Flask-SQLAlchemy.
    """
    # Get the 'page' query parameter from the URL
    page = request.args.get("page", 1, type=int)
    per_page = settings.POSTS_PER_PAGE
    # Calculate the start and end indices of the items to display
    start = (page - 1) * per_page
    end = start + per_page
    # Get the subset of items for the current page
    items = items_to_paginate[start:end]
    # Calculate the total number of pages
    total_pages = len(items_to_paginate) // per_page + (
        1 if len(items_to_paginate) % per_page > 0 else 0
    )
    return items, page, per_page, total_pages


def return_random_quote():
    """
    Description: return a random quote from the dedicated model.
    """
    session = session_commands.get_a_database_session()
    quotes = session.query(Quote).all()
    session.close()
    total_quotes_indexes = len(quotes) - 1
    random_quote = quotes[random.randint(0, total_quotes_indexes)] if len(quotes) > 0 else ""
    return random_quote


def get_random_color(colors_list):
    """
    Description: returns a random element from a list.

    Parameters:
    colors_list -- list, pie chart colors list
    """
    return random.randint(0, len(colors_list) - 1)


def get_pie_colors():
    """
    Description: return the chart's allowed colors.
    """
    colors = []
    colors_list = settings.PIE_COLORS.copy()
    for _ in settings.BOOKS_CATEGORIES:
        color_index = get_random_color(colors_list)
        color = colors_list[color_index]
        colors.append(color)
        colors_list.remove(color)
    return colors


def get_random_books_ids(ids_list, max_ids_to_get):
    """
    Description: return a list of random ids

    Parameters:
    session -- a postgresql'session
    ids_list -- a list of postgresql book's ids
    max_ids_to_get -- integer, specify how many ids we need
    """
    random_ids = set()
    while len(random_ids) < max_ids_to_get:
        random_ids.add(random.choice(ids_list))
    return random_ids


def check_book_fields(book):
    """
    Description: vérifier que l'utilisateur renseigne le livre correctement.
    """
    if any(
        [
            str(book.title).lower() == "string",
            str(book.author).lower() == "string",
            str(book.summary).lower() == "string",
            str(book.content).lower() == "string",
        ]
    ):
        error = "Saisie invalide, mot clef string non utilisable."
        return error
    if not isinstance(book.year_of_publication, int):
        error = "Saisie invalide, annee publication livre doit etre un entier."
        return error
    return True
