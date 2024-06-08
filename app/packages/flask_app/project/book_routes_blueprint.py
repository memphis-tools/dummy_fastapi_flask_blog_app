""" The Book blueprint routes """

import os
from flask import (
    Blueprint,
    url_for,
    render_template,
    flash,
    abort,
    redirect,
    request,
)
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename

from app.packages import log_events, settings
from app.packages.database.commands import session_commands
from app.packages.database.models.models import (
    Book,
    BookCategory,
    Comment,
    Starred,
)
from . import forms
from .shared_functions_and_decorators import (
    return_pagination,
    return_random_quote,
    check_book_fields,
)


book_routes_blueprint = Blueprint("book_routes_blueprint", __name__)


@book_routes_blueprint.route("/books/")
def books():
    """
    Description: the books Flask route.
    """
    session = session_commands.get_a_database_session()
    all_books = (
        session.query(Book)
        .order_by(Book.id)
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .all()
    )
    session.close()
    total_books = len(all_books)
    items, page, per_page, total_pages = return_pagination(all_books)
    random_quote = return_random_quote()
    return render_template(
        "books.html",
        random_quote=random_quote,
        books=items,
        page=page,
        total_books=total_books,
        per_page=per_page,
        total_pages=total_pages,
        is_authenticated=current_user.is_authenticated,
    )


@book_routes_blueprint.route("/book/<int:book_id>/", methods=["GET", "POST"])
@login_required
def book(book_id):
    """
    Description: the book Flask route.
    """
    session = session_commands.get_a_database_session()
    delete_book_form = forms.DeleteInstanceForm()
    form = forms.CommentForm()
    a_book = (
        session.query(Book)
        .filter(Book.id == book_id)
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .first()
    )

    comments = session.query(Comment).filter_by(book_id=a_book.id).all()

    user_starred_books_id_list = (
        session.query(Starred)
        .filter(Starred.user_id == current_user.id)
        .with_entities(Starred.book_id)
        .all()
    )

    logs_context = {
        "current_user": f"{current_user.username}",
        "book_id": book_id,
        "book_title": a_book.title,
    }
    log_events.log_event("[+] Flask - Consultation livre.", logs_context)

    if form.validate_on_submit():
        new_comment = Comment(
            text=form.comment_text.data, author_id=current_user.id, book_id=a_book.id
        )
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": a_book.title,
        }
        log_events.log_event("[+] Flask - Ajout commentaire.", logs_context)
        session.add(new_comment)
        session.commit()
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))

    session.close()
    return render_template(
        "book.html",
        book=a_book,
        user_starred_books_id_list=user_starred_books_id_list,
        form=form,
        delete_book_form=delete_book_form,
        comments=comments,
        is_authenticated=current_user.is_authenticated,
    )


@book_routes_blueprint.route("/books/add/", methods=["GET", "POST"])
@login_required
def add_book():
    """
    Description: the add book Flask route.
    """
    session = session_commands.get_a_database_session()
    books_categories_query = session.query(BookCategory).all()
    books_categories = [(i.id, i.title) for i in books_categories_query]
    form = forms.BookForm(books_categories=books_categories)
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        content = form.content.data
        author = form.author.data
        category_id_from_form = int(form.categories.data[0])
        try:
            category_id = (
                session.query(BookCategory)
                .filter(BookCategory.id == category_id_from_form)
                .first()
                .id
            )
        except Exception:
            flash("Saisie invalide, categorie livre non prevue.", "error")
            return render_template(
                "add_book.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )
        year_of_publication = form.year_of_publication.data
        book_picture = form.photo.data
        filename = secure_filename(book_picture.filename)
        new_book = Book(
            title=title,
            summary=summary,
            content=content,
            author=author,
            category=category_id,
            year_of_publication=year_of_publication,
            book_picture_name=filename,
            user_id=current_user.get_id(),
        )
        book_is_valid = check_book_fields(new_book)
        if book_is_valid is True:
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in settings.UPLOAD_EXTENSIONS:
                    flash("Type image non accepté", "error")
                    return redirect(url_for("index"))
                if os.getenv("SCOPE") == "production":
                    book_picture.save(
                        os.path.join(
                            settings.INSTANCE_PATH, "staticfiles/img", filename
                        )
                    )
                else:
                    new_book.book_picture_name = "dummy_blank_book.png"
                session.add(new_book)
                session.commit()
                session.refresh(new_book)
                session.commit()
                logs_context = {
                    "current_user": f"{current_user.username}",
                    "book_title": new_book.title,
                }
                log_events.log_event("[+] Flask - Ajout livre.", logs_context)
                flash("[+] Flask - Ajout livre.", "info")
                session.close()
                return redirect(url_for("book_routes_blueprint.books"))
        else:
            flash(book_is_valid, "error")
            session.close()
            return render_template(
                "add_book.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )
    session.close()
    return render_template(
        "add_book.html", form=form, is_authenticated=current_user.is_authenticated
    )


@book_routes_blueprint.route("/book/<int:book_id>/delete/", methods=["GET", "POST"])
@login_required
def delete_book(book_id):
    """
    Description: the delete book Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    book_to_delete = session.get(Book, book_id)
    if current_user.id != book_to_delete.user_id and current_user.role != "admin":
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book_to_delete.title,
        }
        log_events.log_event("[+] Flask - Suppression livre refusée.", logs_context)
        flash("Seul l'utilisateur ayant publié le livre peut le supprimer", "error")
        session.close()
        return abort(403)
    if form.validate_on_submit():
        book_picture_name = book_to_delete.book_picture_name
        session.delete(book_to_delete)
        os.remove(f"{settings.INSTANCE_PATH}staticfiles/img/{book_picture_name}")
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book_to_delete.title,
        }
        log_events.log_event("[+] Flask - Suppression livre.", logs_context)
        session.commit()
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))
    session.close()
    return render_template(
        "delete_book.html",
        form=form,
        book_to_delete=book_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


def get_book_by_id(book_id):
    """
    Description: retrieve a book by its ID.
    """
    session = session_commands.get_a_database_session()
    book = (
        session.query(Book)
        .filter(Book.id == book_id)
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .first()
    )
    session.close()
    return book


@book_routes_blueprint.route("/book/<int:book_id>/update/", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    """
    Description: the update book Flask route.
    """
    session = session_commands.get_a_database_session()
    a_book = get_book_by_id(book_id)
    if not a_book:
        flash("Livre non trouvé", "error")
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))

    if current_user.id != a_book.user_id and current_user.role != "admin":
        session.close()
        return abort(403)
    book_picture_filename = a_book.book_picture_name
    books_categories_query = session.query(BookCategory).all()
    books_categories = [(i.id, i.title) for i in books_categories_query]
    edit_form = forms.UpdateBookForm(
        books_categories=books_categories,
        book=a_book,
    )
    if edit_form.validate_on_submit():
        form = request.form.to_dict()
        form_file = request.files.to_dict
        if "title" in form:
            title = form["title"]
        else:
            title = a_book.title
        if "summary" in form:
            summary = form["summary"]
        else:
            summary = a_book.summary
        if "content" in form:
            content = form["content"]
        else:
            content = a_book.content
        if "author" in form:
            author = form["author"]
        else:
            author = a_book.author
        if "year_of_publication" in form:
            year_of_publication = int(form["year_of_publication"])
        else:
            year_of_publication = a_book.year_of_publication
        if "categories" in form:
            category_id_from_form = int(form["categories"])
            try:
                category_id = (
                    session.query(BookCategory)
                    .filter(BookCategory.id == category_id_from_form)
                    .first()
                    .id
                )
            except Exception:
                flash("Saisie invalide, categorie livre non prevue.", "error")
                return render_template(
                    "update_book.html",
                    form=edit_form,
                    is_authenticated=current_user.is_authenticated,
                )
        try:
            book_picture = edit_form["photo"]
            uploaded_file = request.files["photo"]
        except Exception:
            book_picture = None
        if book_picture is not None:
            filename = secure_filename(uploaded_file.filename)
        else:
            filename = book_picture_filename
        publication_date = a_book.publication_date
        updated_book = Book(
            title=title,
            summary=summary,
            content=content,
            author=author,
            category=category_id,
            year_of_publication=year_of_publication,
            book_picture_name=filename,
            publication_date=publication_date,
            user_id=a_book.user_id,
        )
        if book_picture_filename != filename:
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in settings.UPLOAD_EXTENSIONS:
                    return "Image invalide", 400
                if os.getenv("SCOPE") == "production":
                    uploaded_file.save(
                        os.path.join(
                            settings.INSTANCE_PATH, "staticfiles/img", filename
                        )
                    )
                    try:
                        os.remove(
                            f"{settings.INSTANCE_PATH}staticfiles/img/{book_picture_filename}"
                        )
                    except FileNotFoundError:
                        pass
                else:
                    updated_book.book_picture_name = "dummy_blank_book.png"
            else:
                updated_book.book_picture_name = book_picture_filename
        session.query(Book).where(Book.id == book_id).update(
            updated_book.get_json_for_update()
        )
        book_is_valid = check_book_fields(updated_book)
        if book_is_valid is True:
            session.commit()
            session.close()
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": updated_book.title,
            }
            log_events.log_event("[+] Flask - Mise à jour livre.", logs_context)
            flash("[+] Flask - Mise à jour livre.", "info")
            return redirect(url_for("book_routes_blueprint.book", book_id=book_id))

        flash("Erreur avec image illustration", "error")
        session.close()
        return render_template(
            "update_book.html",
            form=edit_form,
            is_authenticated=current_user.is_authenticated,
        )
    return render_template(
        "update_book.html",
        form=edit_form,
        book=a_book,
        is_authenticated=current_user.is_authenticated,
    )
