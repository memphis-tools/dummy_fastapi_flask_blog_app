""" The Book Category blueprint routes """

from flask import (
    Blueprint,
    url_for,
    render_template,
    flash,
    abort,
    redirect,
)
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy.orm import joinedload

from app.packages import log_events
from app.packages.database.commands import session_commands
from app.packages.database.models.models import Book, BookCategory
from . import forms
from .shared_functions_and_decorators import admin_only, return_pagination


book_category_routes_blueprint = Blueprint("book_category_routes_blueprint", __name__)


def check_book_category_fields(category):
    """
    Description: vérifier que l'utilisateur renseigne la catégorie correctement.
    """
    session = session_commands.get_a_database_session()
    if any(
        [
            str(category.title).lower() == "string",
        ]
    ):
        session.close()
        error = "Saisie invalide, mot clef string non utilisable."
        return error
    existing_category = (
        session.query(BookCategory)
        .filter(BookCategory.title == str(category.title).lower())
        .first()
    )
    session.close()
    if existing_category:
        error = "Saisie invalide, categorie existe deja."
        return error
    return True


@book_category_routes_blueprint.route("/front/books/categories/")
def categories():
    """
    Description: the books categories Flask route.
    """
    session = session_commands.get_a_database_session()
    categories_list = []
    categories = session.query(BookCategory).order_by(BookCategory.id).all()
    for category in categories:
        category_id = category.id
        category_books_query = session.query(Book).filter(
            Book.category.in_(
                [
                    category_id,
                ]
            )
        )
        total_category_books = category_books_query.count()
        categories_list.append(
            {"id": category_id, "name": category, "total_books": total_category_books}
        )
    session.close()
    return render_template(
        "categories.html",
        categories_list=categories_list,
        is_authenticated=current_user.is_authenticated,
    )


@book_category_routes_blueprint.route("/front/books/categories/<int:category_id>/")
def category_books(category_id):
    """
    Description: the books from a category Flask route.
    """
    session = session_commands.get_a_database_session()
    category = (
        session.query(BookCategory).filter(BookCategory.id == category_id).first()
    )
    if not category:
        flash(f"Categorie id {category_id} inexistante", "error")
        session.close()
        return redirect(url_for("index"))
    books = (
        session.query(Book)
        .filter(
            Book.category.in_(
                [
                    category_id,
                ]
            )
        )
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .all()
    )
    session.close()
    total_books = len(books)
    items, page, per_page, total_pages = return_pagination(books)
    return render_template(
        "category_books.html",
        category=category,
        books=items,
        page=page,
        total_books=total_books,
        per_page=per_page,
        total_pages=total_pages,
        is_authenticated=current_user.is_authenticated,
    )


@book_category_routes_blueprint.route("/front/categories/", methods=["GET"])
@login_required
@admin_only
def manage_books_categories():
    """
    Description: a manage view to get books categories Flask route.
    """
    session = session_commands.get_a_database_session()
    categories = session.query(BookCategory).all()
    session.close()
    return render_template(
        "books_categories.html",
        categories=categories,
        is_authenticated=current_user.is_authenticated,
    )


@book_category_routes_blueprint.route(
    "/front/book/categories/add/", methods=["GET", "POST"]
)
@login_required
@admin_only
def add_book_category():
    """
    Description: an add book category Flask route.
    """
    form = forms.AddCategoryBookForm()
    if form.validate_on_submit():
        session = session_commands.get_a_database_session()
        title = form.title.data
        new_category = BookCategory(
            title=str(title).lower(),
        )
        category_is_valid = check_book_category_fields(new_category)
        if category_is_valid is True:
            logs_context = {
                "current_user": f"{current_user.username}",
                "new_category": new_category.title,
            }
            log_events.log_event("[+] Flask - Ajout catégorie livre.", logs_context)
            session.add(new_category)
            session.commit()
        else:
            flash(category_is_valid, "error")
        session.close()
        return redirect(
            url_for("book_category_routes_blueprint.manage_books_categories")
        )
    return render_template(
        "add_book_category.html",
        form=form,
        is_authenticated=current_user.is_authenticated,
    )


@book_category_routes_blueprint.route(
    "/front/book/categories/<int:category_id>/delete/", methods=["GET", "POST"]
)
@login_required
@admin_only
def delete_book_category(category_id):
    """
    Description: delete a book category Flask route.
    """
    form = forms.DeleteInstanceForm()
    session = session_commands.get_a_database_session()
    category_to_delete = session.get(BookCategory, category_id)
    if category_to_delete is None:
        flash("Categorie livre non trouvee", "error")
        session.close()
        return abort(404)

    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "category_to_delete": category_to_delete.title,
        }
        log_events.log_event("[+] Flask - Suppression catégorie livre.", logs_context)
        session.delete(category_to_delete)
        session.commit()
        session.close()
        return redirect(
            url_for("book_category_routes_blueprint.manage_books_categories")
        )
    return render_template(
        "delete_book_category.html",
        category_to_delete=category_to_delete,
        form=form,
        is_authenticated=current_user.is_authenticated,
    )


@book_category_routes_blueprint.route(
    "/front/book/categories/<int:category_id>/update/", methods=["GET", "POST"]
)
@login_required
@admin_only
def update_book_category(category_id):
    """
    Description: update a book category Flask route.
    """
    session = session_commands.get_a_database_session()
    category_to_update = session.get(BookCategory, category_id)
    if category_to_update is None:
        flash("Categorie livre non trouvee", "error")
        session.close()
        return abort(404)
    edit_form = forms.UpdateBookCategoryForm(
        title=category_to_update.title,
    )

    if edit_form.validate_on_submit():
        title = edit_form.title.data
        updated_category = BookCategory(
            title=title,
        )
        session.query(BookCategory).where(BookCategory.id == category_id).update(
            updated_category.get_json_for_update()
        )
        book_category_is_valid = check_book_category_fields(updated_category)
        if book_category_is_valid is True:
            logs_context = {
                "current_user": f"{current_user.username}",
                "updated_category_old": category_to_update.title,
                "updated_category_new": updated_category.title,
            }
            log_events.log_event(
                "[+] Flask - Mise à jour catégorie livre.", logs_context
            )
            session.commit()
            session.close()
            return redirect(
                url_for("book_category_routes_blueprint.manage_books_categories")
            )
        else:
            flash(book_category_is_valid, "error")
            session.close()
            return redirect(url_for("index"))
    return render_template(
        "update_book_category.html",
        category_to_update=category_to_update,
        form=edit_form,
        is_authenticated=current_user.is_authenticated,
    )
