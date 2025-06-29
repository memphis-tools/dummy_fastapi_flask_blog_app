""" The Flask app definition.Notice we do not use the app factory pattern """

import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import (
    Flask,
    url_for,
    render_template,
    flash,
    redirect,
    request,
)

from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
)
from flask_wtf import CSRFProtect
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash

try:
    import handle_passwords
    import log_events
    import settings
    from database.commands import session_commands
    from database.models.models import Book, User, BookCategory
except ModuleNotFoundError:
    from app.packages import handle_passwords, log_events, settings
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book, User, BookCategory
from .user_routes_blueprint import user_routes_blueprint
from .stat_routes_blueprint import stat_routes_blueprint
from .book_routes_blueprint import book_routes_blueprint
from .book_category_routes_blueprint import book_category_routes_blueprint
from .comment_routes_blueprint import comment_routes_blueprint
from .quote_routes_blueprint import quote_routes_blueprint
from .shared_functions_and_decorators import get_random_books_ids
from . import forms


app = Flask(
    __name__,
    template_folder="templates",
    instance_path=settings.INSTANCE_PATH,
)
app.config.from_pyfile("config.py")
app.register_blueprint(book_routes_blueprint)
app.register_blueprint(user_routes_blueprint)
app.register_blueprint(stat_routes_blueprint)
app.register_blueprint(book_category_routes_blueprint)
app.register_blueprint(comment_routes_blueprint)
app.register_blueprint(quote_routes_blueprint)

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "/"
login_manager.session_protection = "strong"
WTF_CSRF_SECRET_KEY = app.config["SECRET_KEY"]
MAX_BOOKS_ON_INDEX_PAGE = 3


@login_manager.user_loader
def load_user(user_id):
    """
    Description: a default user_loader which enable the flask_login usage.
    """
    session = session_commands.get_a_database_session()
    loaded = session.get(User, user_id)
    session.close()
    return loaded


@login_manager.unauthorized_handler
def unauthorized():
    """
    Description: disable access to protected uri.
    """
    log_events.log_event("[403] Flask - Utilisateur doit se connecter.")
    flash("Vous devez d'abord vous connecter", "error")
    return redirect(url_for("login"))


@app.errorhandler(413)
def too_large(e):
    """
    Description: custom error message when uploaded image size is too big.
    """
    return f"Taille fichier excède la limite prévue {e}", 413


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
def format_user(user_id):
    """
    Description: a custom filter for username to be used in templates
    """
    session = session_commands.get_a_database_session()
    user = session.get(User, user_id)
    session.close()
    if current_user.is_authenticated:
        if current_user.id == user.id:
            return "vous"
    return user


@app.template_filter()
def format_book_category(book_id):
    """
    Description: a custom filter for book category to be used in templates
    """
    session = session_commands.get_a_database_session()
    category = session.get(BookCategory, book_id)
    session.close()
    return category


@app.route("/")
@app.route("/home/")
def index():
    """
    Description: the index /home, Flask route.
    """
    session = session_commands.get_a_database_session()
    ids_list = [id[0] for id in session.query(Book.id).all()]
    if len(ids_list) >= MAX_BOOKS_ON_INDEX_PAGE:
        random_ids = get_random_books_ids(ids_list, MAX_BOOKS_ON_INDEX_PAGE)
    else:
        random_ids = get_random_books_ids(ids_list, len(ids_list))
    first_books = (
        session.query(Book)
        .filter(Book.id.in_(random_ids))
        .options(joinedload(Book.book_comments))
        .options(joinedload(Book.starred))
        .all()
    )
    session.close()
    return render_template(
        "index.html", books=first_books, is_authenticated=current_user.is_authenticated
    )


@app.route("/contact/", methods=["GET", "POST"])
def contact():
    """
    Description: the contact Flask route.
    """
    form = forms.ContactForm()
    if form.validate_on_submit():
        # Retrieve hCaptcha response token from the form data
        hcaptcha_response = request.form.get('h-captcha-response')
        if not hcaptcha_response:
            flash("Veuillez valider le captcha.", "error")
            return render_template("contact.html", form=form)

        # hCaptcha verification
        hcaptcha_secret_key = app.config["HCAPTCHA_SITE_SECRET"]
        verify_url = app.config["HCAPTCHA_VERIFY_URL"]
        payload = {
            "secret": hcaptcha_secret_key,
            "response": hcaptcha_response
        }

        # Make POST request to hCaptcha API
        response = requests.post(verify_url, data=payload)
        response_json = response.json()

        if not response_json.get('success'):
            flash("Echec vérification hCaptcha, essayez de nouveau.", "error")
            return render_template(
                "contact.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )
        username = form.name.data
        email = form.email.data
        message = form.message.data

        message = Mail(
            from_email="no-reply@dummy-ops.dev",
            to_emails=f'{app.config["ADMIN_EMAIL"]}',
            subject="Dummy-ops contact",
            html_content=f"{username} with email {email} sent this message: {message}"
        )

        try:
            sg = SendGridAPIClient(app.config["SENDGRID_API_KEY"])
            sg.send(message)
            return render_template(
                "mail_sent.html",
                name=username,
                is_authenticated=current_user.is_authenticated,
            )
        except Exception as e:
            logs_context = {"username": f"{username}", "email": f"{email}"}
            log_events.log_event(
                f"[400] Flask - Echec envoi email: {e}", logs_context
            )
            return render_template(
                "mail_not_sent.html",
                name=username,
                is_authenticated=current_user.is_authenticated,
            )
    return render_template(
        "contact.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/login/", methods=["GET", "POST"])
def login():
    """
    Description: the login Flask route.
    Ensure the email is well formed (in database).
    """
    session = session_commands.get_a_database_session()
    form = forms.LoginForm()
    if form.validate_on_submit():
        # Retrieve hCaptcha response token from the form data
        hcaptcha_response = request.form.get('h-captcha-response')
        if not hcaptcha_response:
            flash("Veuillez valider le captcha.", "error")
            return render_template("login.html", form=form)

        # hCaptcha verification
        hcaptcha_secret_key = app.config["HCAPTCHA_SITE_SECRET"]
        verify_url = app.config["HCAPTCHA_VERIFY_URL"]
        payload = {
            "secret": hcaptcha_secret_key,
            "response": hcaptcha_response
        }

        # Make POST request to hCaptcha API
        response = requests.post(verify_url, data=payload)
        response_json = response.json()

        email = str(form.email.data).lower()
        username = str(form.login.data).lower()
        password = form.password.data
        user = session.query(User).filter_by(username=username).first()
        if not user or user.email != email:
            logs_context = {"username": f"{username}", "email": f"{email}"}
            log_events.log_event(
                "[400] Flask - Echec connexion à application.", logs_context
            )
            flash("Identifiants invalides", "error")
            session.close()
            return redirect(url_for("index"))

        if not response_json.get('success'):
            logs_context = {"username": f"{username}", "email": f"{email}"}
            log_events.log_event(
                "[400] Flask - Echec vérification hCaptcha.", logs_context
            )
            flash("Echec vérification hCaptcha, essayez de nouveau.", "error")
            session.close()
            return render_template(
                "login.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )

        if check_password_hash(user.hashed_password, password):
            login_user(user)
            flash(f"Vous nous avez manqué {user} 🫶")
            logs_context = {"username": f"{username}"}
            log_events.log_event("[200] Flask - Connexion à application.", logs_context)
            session.close()
            return redirect(url_for("index"))

        logs_context = {"username": f"{username}", "email": f"{email}"}
        log_events.log_event(
            "[400] Flask - Echec connexion à application. Mot de passe invalide.",
            logs_context,
        )
        flash("Mot de passe invalide", "error")
        session.close()
    return render_template(
        "login.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/logout/")
def logout():
    """
    Description: the logout Flask route.
    """
    logout_user()
    flash("Vous n'êtes plus connecté 👋")
    return redirect(url_for("index"))


@app.route("/register/", methods=["GET", "POST"])
def register():
    """
    Description: the register Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.RegisterForm()
    if form.validate_on_submit():
        # Retrieve hCaptcha response token from the form data
        hcaptcha_response = request.form.get('h-captcha-response')
        if not hcaptcha_response:
            flash("Veuillez valider le captcha.", "error")
            return render_template("register.html", form=form)

        # hCaptcha verification
        hcaptcha_secret_key = app.config["HCAPTCHA_SITE_SECRET"]
        verify_url = app.config["HCAPTCHA_VERIFY_URL"]
        payload = {
            "secret": hcaptcha_secret_key,
            "response": hcaptcha_response
        }

        # Make POST request to hCaptcha API
        response = requests.post(verify_url, data=payload)
        response_json = response.json()

        if not response_json.get('success'):
            flash("Echec vérification hCaptcha, essayez de nouveau.", "error")
            session.close()
            return render_template(
                "register.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )

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
            flash("Email existe déjà en base", "error")
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
                log_events.log_event(
                    "[201] Flask - Création compte utilisateur.", logs_context
                )
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
                flash("Email existe déjà en base", "error")
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
                    log_events.log_event(
                        "[201] Flask - Création compte utilisateur.", logs_context
                    )
                    session.close()
                    return redirect(url_for("login"))
                logs_context = {"username": f"{username}", "email": f"{email}"}
                log_events.log_event(
                    "[400] Nom utilisateur existe déjà, veuillez le modifier.", logs_context
                )
                flash("Nom utilisateur existe déjà, veuillez le modifier", "error")
    session.close()
    return render_template(
        "register.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/ops/")
def ops():
    """
    Description: the ops Flask route.
    """
    return render_template("ops.html", is_authenticated=current_user.is_authenticated)


@app.route("/moocs/")
def moocs():
    """
    Description: the moocs Flask route.
    """
    return render_template("moocs.html", is_authenticated=current_user.is_authenticated)
