""" The User blueprint routes """

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
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import handle_passwords
    import log_events
    from database.commands import session_commands
    from database.models.models import Book, User, Starred
except ModuleNotFoundError:
    from app.packages import handle_passwords, log_events
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book, User, Starred
from . import forms
from .shared_functions_and_decorators import admin_only, return_pagination

user_routes_blueprint = Blueprint("user_routes_blueprint", __name__)


@user_routes_blueprint.route("/users/", methods=["GET"])
@login_required
@admin_only
def users():
    """
    Description: the users app Flask route.
    """
    session = session_commands.get_a_database_session()
    # remember that user with id 1 is the application admin (wr remove it from dataset)
    all_users = session.query(User).all()[1:]
    session.close()
    return render_template(
        "users.html", users=all_users, is_authenticated=current_user.is_authenticated
    )


@user_routes_blueprint.route("/users/add/", methods=["GET", "POST"])
@login_required
@admin_only
def add_user():
    """
    Description: the add user Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.CreateUserForm()
    if form.validate_on_submit():
        if not handle_passwords.check_password(form.password.data):
            flash("Mot de passe trop simple, essayez de nouveau.", "error")
            session.close()
            return render_template(
                "register.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )
        username = str(form.login.data).lower()
        hashed_password = generate_password_hash(
            form.password.data, "pbkdf2:sha256", salt_length=8
        )
        email = str(form.email.data).lower()
        user = session.query(User).filter_by(username=username).first()
        user_email = session.query(User).filter_by(email=email).first()
        if user_email:
            flash("Email existe deja en base", "error")
        elif form.password.data != form.password_check.data:
            flash("Mots de passe ne correspondent pas", "error")
        else:
            if not user:
                new_user = User(
                    username=username, hashed_password=hashed_password, email=email
                )
                session.add(new_user)
                session.commit()
                flash(f"Creation utilisateur {username} faite", "info")
                logs_context = {"username": f"{username}", "email": f"{email}"}
                log_events.log_event(
                    "[200] Flask - Création compte utilisateur par admin.", logs_context
                )
                session.close()
                return redirect(url_for("login"))
            flash("Nom utilisateur existe deja, veuillez le modifier", "error")
    session.close()
    return render_template(
        "add_user.html", form=form, is_authenticated=current_user.is_authenticated
    )


@user_routes_blueprint.route("/user/<int:user_id>/delete/", methods=["GET", "POST"])
@login_required
@admin_only
def delete_user(user_id):
    """
    Description: the delete user Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    user_to_delete = session.get(User, user_id)
    if user_id == 1:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event("[403] Flask - Suppression compte admin refusée.", logs_context)
        session.close()
        return abort(403)
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "user_to_delete": user_to_delete.username,
        }
        log_events.log_event("[204] Flask - Suppression utilisateur.", logs_context)
        session.delete(user_to_delete)
        session.commit()
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))
    session.close()
    return render_template(
        "delete_user.html",
        form=form,
        user_to_delete=user_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@user_routes_blueprint.route("/users/password/", methods=["GET", "POST"])
@login_required
def update_password():
    """
    Description: the update user password Flask route.
    """
    form = forms.UpdateUserPasswordForm()
    username = current_user.username
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        new_password_check = form.new_password_check.data
        if not check_password_hash(current_user.hashed_password, current_password):
            flash("Mot de passe actuel ne correspond pas.")
        elif not handle_passwords.check_password_input(
            current_password, new_password, new_password_check
        ):
            flash("Champs attendus non saisis.")
        elif not handle_passwords.check_password(new_password):
            flash("Mot de passe trop simple, essayez de nouveau.")
        elif new_password != new_password_check:
            flash("Mots de passes ne correspondent pas.")
        else:
            session = session_commands.get_a_database_session()
            hashed_password = generate_password_hash(
                new_password, "pbkdf2:sha256", salt_length=8
            )
            updated_user = User(
                username=current_user.username,
                hashed_password=hashed_password,
                email=current_user.email,
                role=current_user.role,
            )
            session.query(User).where(User.id == current_user.id).update(
                updated_user.get_json_for_update()
            )
            session.commit()
            logs_context = {
                "current_user": f"{current_user.username}",
            }
            log_events.log_event("[200] Flask - Mot de passe mis à jour.", logs_context)
            flash(f"Mot de passe mis a jour {current_user} 💪")
            session.close()
        return redirect(url_for("index"))
    return render_template(
        "update_password.html",
        form=form,
        username=username,
        is_authenticated=current_user.is_authenticated,
    )


@user_routes_blueprint.route("/user/<int:user_id>/books/")
@login_required
def user_books(user_id):
    """
    Description: the user's book Flask route.
    """
    session = session_commands.get_a_database_session()
    user = session.get(User, user_id)
    if not user:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event("[404] Flask - Recherche livres utilisateur inconnu.", logs_context)
        flash(f"Utilisateur id {user_id} inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    books = (
        session.query(Book)
        .filter(
            Book.user_id.in_(
                [
                    user_id,
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
    if current_user.id == user_id:
        return render_template(
            "user_books.html",
            books=items,
            page=page,
            total_books=total_books,
            per_page=per_page,
            total_pages=total_pages,
            user_name=user.username,
            user_id=user.id,
            is_authenticated=current_user.is_authenticated,
        )

    return render_template(
        "user_any_books.html",
        books=items,
        page=page,
        total_books=total_books,
        per_page=per_page,
        total_pages=total_pages,
        user_name=user.username,
        user_id=user.id,
        is_authenticated=current_user.is_authenticated,
    )


@user_routes_blueprint.route("/users/<int:user_id>/starred/")
@login_required
def user_starred(user_id):
    """
    Description: a user's book starred Flask route.
    As soon as an user is authenticated he should be able to consult his starred books
    and those from any existing users.
    """
    session = session_commands.get_a_database_session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event("[404] Flask - Recherche livres favoris d'un utilisateur inconnu.", logs_context)
        flash(f"Utilisateur id {user_id} inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    books = (
        session.query(Book)
        .join(Starred)
        .filter(Book.id == Starred.book_id)
        .filter(Starred.user_id == user_id)
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .all()
    )
    session.close()
    total_books = len(books)
    items, page, per_page, total_pages = return_pagination(books)
    return render_template(
        "books_starred.html",
        books=items,
        page=page,
        total_books=total_books,
        per_page=per_page,
        total_pages=total_pages,
        user=user,
        is_authenticated=current_user.is_authenticated,
    )


@user_routes_blueprint.route(
    "/users/<int:user_id>/books/<int:book_id>/starred/delete/",
    methods=["GET", "POST"],
)
@login_required
def delete_starred_book(user_id, book_id):
    """
    Description: the remove starred book Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        flash("Utilisateur inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    starred_book_to_delete = (
        session.query(Starred)
        .filter(Starred.book_id == book_id)
        .filter(Starred.user_id == user_id)
        .first()
    )
    if not starred_book_to_delete:
        flash("Favori inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    if not user_id == current_user.id:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event("[403] Flask - Utilisateur veut supprimer favoris d'un autre utilisateur.", logs_context)
        flash("Vous ne pouvez supprimer que vos favoris", "error")
        session.close()
        return redirect(url_for("index"))
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "starred_book_deleted": starred_book_to_delete,
        }
        log_events.log_event("[204] Flask - Suppression favori.", logs_context)
        session.delete(starred_book_to_delete)
        session.commit()
        flash("Favori supprimé", "info")
        session.close()
        return redirect(
            url_for(
                "book_routes_blueprint.book",
                book_id=starred_book_to_delete.id,
                is_authenticated=current_user.is_authenticated,
            )
        )
    return render_template(
        "delete_starred_book.html",
        form=form,
        book_to_delete=starred_book_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@user_routes_blueprint.route(
    "/users/<int:user_id>/books/<int:book_id>/starred/add/",
    methods=["GET", "POST"],
)
@login_required
def add_starred_book(user_id, book_id):
    """
    Description: the add starred book Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.AddInstanceForm()
    starred_book_to_add = (
        session.query(Starred)
        .filter(Starred.book_id == book_id)
        .filter(Starred.user_id == user_id)
        .first()
    )

    if starred_book_to_add:
        flash("Vous avez deja ce livre en favori", "error")
        session.close()
        return redirect(
            url_for(
                "index",
                is_authenticated=current_user.is_authenticated,
            )
        )

    if not user_id == current_user.id:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event("[403] Flask - Utilisateur veut ajouter un favori pour un autre utilisateur.", logs_context)
        flash("Vous ne pouvez ajouter que vos favoris", "error")
        session.close()
        return redirect(url_for("index"))

    if form.validate_on_submit():
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            logs_context = {
                "current_user": f"{current_user.username}",
            }
            log_events.log_event("[404] Flask - Ajout en favori d'un livre inconnu.", logs_context)
            flash("Livre inexistant", "error")
            session.close()
            return redirect(url_for("index"))
        new_starred_book = Starred(
            user_id=current_user.id,
            book_id=book_id,
        )
        logs_context = {
            "current_user": f"{current_user.username}",
            "starred_book_added": book,
        }
        log_events.log_event("[200] Flask - Ajout favori.", logs_context)
        session.add(new_starred_book)
        session.commit()
        session.close()
        flash("Livre en favori", "info")
        return redirect(
            url_for(
                "book_routes_blueprint.book",
                book_id=book_id,
                is_authenticated=current_user.is_authenticated,
            )
        )
    session.close()
    return render_template(
        "add_starred_book.html",
        form=form,
        book_to_add=starred_book_to_add,
        is_authenticated=current_user.is_authenticated,
    )
