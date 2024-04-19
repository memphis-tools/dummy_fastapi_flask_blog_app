"""
The Flask app definition.Notice we do not use the app factory pattern
"""

import os
from functools import wraps
from flask import Flask, url_for, render_template, flash, abort, redirect, request
from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


try:
    from app.packages import logtail_handler, settings
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book, Comment, User, BookCategory
except ModuleNotFoundError:
    from packages import logtail_handler, settings
    from packages.database.commands import session_commands
    from packages.database.models.models import Book, Comment, User, BookCategory

from . import forms


app = Flask(
    __name__,
    template_folder="templates",
    instance_path="/home/dummy-operator/flask/",
)
app.config.from_pyfile("config.py")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "/"
login_manager.session_protection = "strong"
WTF_CSRF_SECRET_KEY = os.getenv("SECRET_KEY")
MAX_BOOKS_ON_INDEX_PAGE = 3
LOGGER = logtail_handler.logger


@login_manager.user_loader
def load_user(user_id):
    """
    Description: a default user_loader which enable the flask_login usage.
    """
    session = session_commands.get_a_database_session("postgresql")
    loaded = session.get(User, user_id)
    session.close()
    return loaded


@login_manager.unauthorized_handler
def unauthorized():
    """
    Description: disable access to protected uri.
    """
    flash("Vous devez d'abord vous connecter", "error")
    return redirect(url_for("login"))


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


@app.template_filter()
def format_datetime(value):
    """
    Description: a custom filter for date to be used in templates
    """
    # to use for an english output (import calendar)
    # formated_date = f"{calendar.month_name[int(value.strftime('%m'))]} {value.strftime('%d')} {value.strftime('%Y')}"
    formated_date = (
        f"{value.strftime('%d')}/{value.strftime('%m')}/{value.strftime('%Y')}"
    )
    return formated_date


@app.template_filter()
def format_user(id):
    """
    Description: a custom filter for username to be used in templates
    """
    session = session_commands.get_a_database_session("postgresql")
    user = session.get(User, id)
    session.close()
    if current_user.is_authenticated:
        if current_user.id == user.id:
            return "vous"
    return user


@app.template_filter()
def format_book_category(id):
    """
    Description: a custom filter for book category to be used in templates
    """
    session = session_commands.get_a_database_session("postgresql")
    category = session.get(BookCategory, id)
    session.close()
    return category


@app.route("/front")
@app.route("/front/home/")
def index():
    """
    Description: the index /home, Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    first_books = session.query(Book).order_by("id").all()[:MAX_BOOKS_ON_INDEX_PAGE]
    session.close()
    return render_template(
        "index.html", books=first_books, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/contact/", methods=["GET", "POST"])
def contact():
    """
    Description: the contact Flask route.
    """
    form = forms.ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        debug_level = os.getenv("LOGGING_LEVEL")
        if os.getenv("EMAIL_SERVER") == "localhost":
            file_path = os.getenv("LOCAL_EMAIL_LOGS_FILE")
            with open(file_path, "a") as fd:
                fd.write(f"{debug_level}: MAIL FROM {email}| aka {name}: {message}\n")
            return render_template(
                "mail_sent.html",
                name=name,
                is_authenticated=current_user.is_authenticated,
            )
        return render_template(
            "mail_not_sent.html",
            name=name,
            is_authenticated=current_user.is_authenticated,
        )
    return render_template(
        "contact.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/books/")
def books():
    """
    Description: the books Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    books = session.query(Book).order_by(Book.id).all()
    session.close()
    return render_template(
        "books.html", books=books, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/book/<int:book_id>/", methods=["GET", "POST"])
@login_required
def book(book_id):
    """
    Description: the book Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    delete_book_form = forms.DeleteBookForm()
    form = forms.CommentForm()
    book = session.get(Book, book_id)
    comments = session.query(Comment).filter_by(book_id=book.id).all()

    logs_context = {
        "current_user": f"{current_user.username}",
        "book_id": book_id,
        "book_title": book.title
    }
    LOGGER.info("[+] Flask - Consultation livre", extra=logs_context)

    if request.method == "POST":
        if form.validate_on_submit():
            new_comment = Comment(
                text=form.comment_text.data, author_id=current_user.id, book_id=book.id
            )
            total_book_comments = book.nb_comments + 1
            book.nb_comments = total_book_comments
            logs_context = {"current_user": f"{current_user.username}", "book_title": book.title}
            LOGGER.info("[+] Flask - Ajout commentaire.", extra=logs_context)
            session.add(new_comment)
            session.commit()
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "book.html",
        book=book,
        form=form,
        delete_book_form=delete_book_form,
        comments=comments,
        is_authenticated=current_user.is_authenticated,
    )


def check_book_fields(book):
    """
    Description: vérifier que l'utilisateur renseigne le livre correctement.
    """
    if any([
        book.title == "string",
        book.author == "string",
        book.summary == "string",
        book.content == "string",
    ]):
        error = "Saisie invalide, mot clef string non utilisable."
        return error
    if type(book.year_of_publication) is not int:
        error = "Saisie invalide, annee publication livre doit etre un entier."
        return error
    return True


@app.route("/front/add_book/", methods=["GET", "POST"])
@login_required
def add_book():
    """
    Description: the add book Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    form = forms.BookForm()
    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        content = form.content.data
        author = form.author.data
        category = form.categories.data[0]["intitule"]
        try:
            category_id = session.query(BookCategory).filter(BookCategory.title==category).first().id
        except Exception:
            flash("Saisie invalide, categorie livre non prevue.", "error")
            return render_template(
                "add_book.html", form=form, is_authenticated=current_user.is_authenticated
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
            if os.getenv("SCOPE") == "production":
                book_picture.save(os.path.join(app.instance_path, "staticfiles", filename))
            session.add(new_book)
            session.commit()
            session.refresh(new_book)
            user = session.get(User, new_book.user_id)
            total_user_publications = user.nb_publications + 1
            user.nb_publications = total_user_publications
            session.commit()
            logs_context = {"current_user": f"{current_user.username}", "book_title": new_book.title}
            LOGGER.info("[+] Flask - Ajout livre", extra=logs_context)
            session.close()
            return redirect(url_for("books"))
        else:
            flash(book_is_valid, "error")
            session.close()
            return render_template(
            "add_book.html", form=form, is_authenticated=current_user.is_authenticated
            )
    session.close()
    return render_template(
        "add_book.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/login/", methods=["GET", "POST"])
def login():
    """
    Description: the login Flask route.
    Ensure the email is well formed (in database).
    """
    form = forms.LoginForm()
    if form.validate_on_submit():
        session = session_commands.get_a_database_session("postgresql")
        email = form.email.data
        username = form.login.data
        password = form.password.data
        user = session.query(User).filter_by(username=username).first()
        if not user or user.email != email:
            logs_context = {"username": f"{username}", "email": f"{email}"}
            LOGGER.info("[+] Flask - Echec connexion à application.", extra=logs_context)
            flash("Identifiants invalides", "error")
        else:
            if check_password_hash(user.hashed_password, password):
                login_user(user)
                first_books = session.query(Book).order_by("id").all()[:3]
                flash(f"Vous nous avez manqué {user} 🫶")
                logs_context = {"username": f"{username}"}
                LOGGER.info("[+] Flask - Connexion à application.", extra=logs_context)
                session.close()
                return render_template(
                    "index.html",
                    books=first_books,
                    is_authenticated=current_user.is_authenticated,
                )
            else:
                logs_context = {"username": f"{username}", "email": f"{email}"}
                LOGGER.info("[+] Flask - Echec connexion à application. Mot de passe invalide.", extra=logs_context)
                flash("Mot de passe invalide", "error")
        session.close()
    return render_template(
        "login.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/logout/")
def logout():
    """
    Description: the logout Flask route.
    """
    logout_user()
    flash("Vous n'êtes plus connecté 👋")
    return redirect(url_for("index"))


@app.route("/front/register/", methods=["GET", "POST"])
def register():
    """
    Description: the register Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    form = forms.RegisterForm()
    if form.validate_on_submit():
        if any([
            form.login.data == "string",
            form.email.data == "string",
            form.password.data == "string",
            form.password_check.data == "string"
        ]):
            flash("Saisie invalide, mot clef string non utilisable.", "error")
            session.close()
            return render_template(
                "register.html", form=form, is_authenticated=current_user.is_authenticated
            )
        username = form.login.data
        hashed_password = generate_password_hash(
            form.password.data, "pbkdf2:sha256", salt_length=8
        )
        email = form.email.data
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
                flash(f"Bienvenue {username} vous pouvez vous connecter", "info")
                logs_context = {"username": f"{username}", "email": f"{email}"}
                LOGGER.info("[+] Flask - Création compte utilisateur.", extra=logs_context)
                session.close()
                return redirect(url_for("login"))
            else:
                flash("Nom utilisateur existe deja, veuillez le modifier", "error")
    session.close()
    return render_template(
        "register.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/comment/<int:comment_id>/update/", methods=["GET", "POST"])
@login_required
def update_comment(comment_id):
    """
    Description: the update comment Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    comment = session.get(Comment, comment_id)
    edit_form = forms.UpdateCommentForm(
        comment_text=comment.text,
    )
    if current_user.id != comment.author_id and current_user.role != "admin":
        session.close()
        return abort(403)
    if edit_form.validate_on_submit():
        comment.text = edit_form.comment_text.data
        session.commit()
        flash("Commentaire mis a jour", "info")
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "update_comment.html",
        form=edit_form,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/book/<int:book_id>/update/", methods=["GET", "POST"])
@login_required
def update_book(book_id):
    """
    Description: the update book Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    book = session.get(Book, book_id)
    category = session.query(BookCategory).filter(BookCategory.id==book.category).first()
    if book:
        book_picture_filename = book.book_picture_name
        edit_form = forms.UpdateBookForm(
            title=book.title,
            summary=book.summary,
            content=book.content,
            category=book.category,
            year_of_publication=book.year_of_publication,
            author=book.author,
        )
        if edit_form.validate_on_submit():
            title = edit_form.title.data
            summary = edit_form.summary.data
            content = edit_form.content.data
            author = edit_form.author.data
            category = edit_form.categories.data[0]["intitule"]
            category_id = session.query(BookCategory).filter(BookCategory.title==category).first().id
            year_of_publication = edit_form.year_of_publication.data
            book_picture = edit_form.photo.data
            if book_picture is not None:
                filename = secure_filename(book_picture.filename)
            else:
                filename = book_picture_filename
            publication_date = book.publication_date
            updated_book = Book(
                title=title,
                summary=summary,
                content=content,
                author=author,
                category=category_id,
                year_of_publication=year_of_publication,
                book_picture_name=filename,
                publication_date=publication_date,
                user_id=book.user_id,
            )
            if book_picture_filename != filename:
                book_picture.save(os.path.join(app.instance_path, "staticfiles", filename))
                try:
                    os.remove(f"{app.instance_path}staticfiles/{book_picture_filename}")
                except FileNotFoundError:
                    pass
            book_is_valid = check_book_fields(updated_book)
            if book_is_valid is True:
                session.query(Book).where(Book.id == book_id).update(
                    updated_book.get_json_for_update()
                )
                session.commit()
                session.close()
                return redirect(url_for("book", book_id=book.id))
            else:
                flash(book_is_valid, "error")
                session.close()
                return render_template(
                "update_book.html", form=edit_form, is_authenticated=current_user.is_authenticated
                )
    else:
        flash("Livre non trouvé", "error")
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "update_book.html",
        form=edit_form,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/users/", methods=["GET"])
@login_required
@admin_only
def users():
    """
    Description: the users app Flask route.
    """
    if current_user.role != "admin":
        return abort(401)
    else:
        session = session_commands.get_a_database_session("postgresql")
        # remember that user with id 1 is the application admin (wr remove it from dataset)
        users = session.query(User).all()[1:]
        session.close()
        return render_template(
            "users.html", users=users, is_authenticated=current_user.is_authenticated
        )


@app.route("/front/book//<int:book_id>/delete/", methods=["GET", "POST"])
@login_required
def delete_book(book_id):
    """
    Description: the delete book Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    form = forms.DeleteBookForm()
    book_to_delete = session.get(Book, book_id)
    user = session.get(User, book_to_delete.user_id)
    if current_user.id != book_to_delete.user_id and current_user.role != "admin":
        logs_context = {"current_user": f"{current_user.username}", "book_title": book_to_delete.title}
        LOGGER.info("[+] Flask - Suppression livre refusée", extra=logs_context)
        flash("Seul l'utilisateur ayant publié le livre peut le supprimer", "error")
        session.close()
        return abort(403)
    if form.validate_on_submit():
        book_picture_name = book_to_delete.book_picture_name
        session.delete(book_to_delete)
        os.remove(f"{app.instance_path}staticfiles/{book_picture_name}")
        total_user_publications = user.nb_publications - 1
        user.nb_publications = total_user_publications
        logs_context = {"current_user": f"{current_user.username}", "book_title": book_to_delete.title}
        LOGGER.info("[+] Flask - Suppression livre", extra=logs_context)
        session.commit()
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "delete_book.html",
        form=form,
        book_to_delete=book_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/comment/<int:comment_id>/delete/", methods=["GET", "POST"])
@login_required
def delete_comment(comment_id):
    """
    Description: the delete comment Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    form = forms.DeleteCommentForm()
    comment_to_delete = session.get(Comment, comment_id)
    book = session.get(Book, comment_to_delete.book_id)
    if current_user.id != comment_to_delete.author_id and current_user.role != "admin":
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book.title,
            "comment": comment_to_delete.text
        }
        LOGGER.info("[+] Flask - Suppression commentaire refusée", extra=logs_context)
        flash("Seul l'auteur du commentaire peut le supprimer", "error")
        session.close()
        return abort(403)
    if form.validate_on_submit():
        session.delete(comment_to_delete)
        total_book_comments = book.nb_comments - 1
        book.nb_comments = total_book_comments
        session.commit()
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "delete_comment.html",
        form=form,
        comment_to_delete=comment_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/user/<int:user_id>/delete/", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    """
    Description: the delete user Flask route.
    """
    session = session_commands.get_a_database_session("postgresql")
    form = forms.DeleteUserForm()
    user_to_delete = session.get(User, user_id)
    if user_id == 1:
        session.close()
        flash("Le compte admin ne peut pas etre supprime", "error")
        return abort(403)
    if current_user.id != 1:
        logs_context = {
            "current_user": f"{current_user.username}",
            "user_to_delete": user_to_delete.username
        }
        LOGGER.info(
            "[+] Flask - Suppression utilisateur refusée, utilisateur non admin",
            extra=logs_context
        )
    if form.validate_on_submit():
        session.delete(user_to_delete)
        session.commit()
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "delete_user.html",
        form=form,
        user_to_delete=user_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/ops/")
def ops():
    """
    Description: the ops Flask route.
    """
    return render_template(
        "ops.html", is_authenticated=current_user.is_authenticated
    )


@app.route("/front/moocs/")
def moocs():
    """
    Description: the moocs Flask route.
    """
    return render_template(
        "moocs.html", is_authenticated=current_user.is_authenticated
    )
