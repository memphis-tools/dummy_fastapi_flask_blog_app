""" The Flask app definition.Notice we do not use the app factory pattern """

import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from markupsafe import escape
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
from itsdangerous import URLSafeTimedSerializer

try:
    import handle_passwords
    import log_events
    import settings
    from database.commands import session_commands
    from database.models.models import Book, User, BookCategory
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages import handle_passwords, log_events, settings
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book, User, BookCategory
    from app.packages.utils import get_secret
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
CONTACT_TOKEN_SALT = "contact-confirmation"
CONTACT_TOKEN_MAX_AGE = 86400  # 1 jour
SENDGRID_API_KEY = get_secret("/run/secrets/SENDGRID_API_KEY")
WTF_CSRF_SECRET_KEY = app.config["SECRET_KEY"]
MAX_BOOKS_ON_INDEX_PAGE = 3
sengrid_tokens_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)



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
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    path = request.path
    method = request.method

    log_events.log_event(
        f"[401] Flask - Utilisateur doit se connecter | IP={ip} | "
        f"Method={method} | Path={path}"
    )

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


def _send_email(to_email, subject, html_content):
    """
    Description: send an email via SendGrid (production) or Mailtrap (development).
    """
    if os.getenv("SCOPE") == "production":
        message = Mail(
            from_email="no-reply@dummy-ops.dev",
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    elif os.getenv("SCOPE") == "development":
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = to_email
        msg["From"] = "no-reply@dummy-ops.dev"
        msg.attach(MIMEText(html_content, "html"))
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login(
                os.getenv("MAILTRAP_USER_NAME"),
                os.getenv("MAILTRAP_USER_PASSWORD"),
            )
            server.send_message(msg, "no-reply@dummy-ops.dev", [to_email])


def send_contact_validation_link(name, email, message):
    """
    Description: email the visitor a signed link to validate their email address
    before their contact message is forwarded to the admin.
    """
    token = sengrid_tokens_serializer.dumps(
        {"name": name, "email": email, "message": message},
        salt=CONTACT_TOKEN_SALT,
    )
    confirm_url = url_for("confirm_contact", token=token, _external=True)
    _send_email(
        email,
        "Dummy-ops - validez votre message de contact",
        f"""
        <p>Bonjour {escape(name)},</p>
        <p>Cliquez sur le lien pour valider votre adresse email et envoyer votre message :</p>
        <p><a href="{confirm_url}">Valider mon message</a></p>
        """,
    )
    


def forward_contact_message(name, email, message):
    """
    Description: forward the validated contact message to the admin inbox.
    """
    _send_email(
        get_secret("/run/secrets/ADMIN_EMAIL"),
        "Dummy-ops contact",
        f"<p>{escape(name)} ({escape(email)}) a envoyé ce message : {escape(message)}</p>",
    )


@app.route("/contact/confirm/<token>")
def confirm_contact(token):
    """
    Description: validates the visitor's email via the signed token, then
    forwards the contact message to the admin.
    """
    try:
        payload = sengrid_tokens_serializer.loads(
            token, salt=CONTACT_TOKEN_SALT, max_age=CONTACT_TOKEN_MAX_AGE
        )
        name = payload["name"]
        email = payload["email"]
        message = payload["message"]
    except Exception:
        flash("Le lien de validation n'est pas valide ou a expiré.", "error")
        return redirect(url_for("contact"))

    try:
        forward_contact_message(name, email, message)
    except Exception as e:
        app.logger.exception("Echec envoi du message contact après validation")
        log_events.log_event(
            f"[400] Flask - Echec envoi du message contact après validation: {e}",
            {"username": name, "email": email},
        )
        return render_template(
            "mail_not_sent.html",
            name=name,
            is_authenticated=current_user.is_authenticated,
        )

    log_events.log_event(
        "[200] Flask - Message de contact transmis après validation de l'email.",
        {"username": name, "email": email},
    )
    return render_template(
        "mail_sent.html",
        name=name,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/contact/", methods=["GET", "POST"])
def contact():
    """
    Description: the contact Flask route. Sends the visitor a validation email;
    the message reaches the admin only after the email is confirmed.
    """
    form = forms.ContactForm()
    if form.validate_on_submit():
        hcaptcha_response = request.form.get('h-captcha-response')
        if not hcaptcha_response:
            flash("Veuillez valider le captcha.", "error")
            return render_template("contact.html", form=form)

        hcaptcha_secret_key = app.config["HCAPTCHA_SITE_SECRET"]
        verify_url = app.config["HCAPTCHA_VERIFY_URL"]
        payload = {
            "secret": hcaptcha_secret_key,
            "response": hcaptcha_response
        }
        response = requests.post(verify_url, data=payload)
        response_json = response.json()

        if not response_json.get('success'):
            flash("Echec vérification hCaptcha, essayez de nouveau.", "error")
            return render_template(
                "contact.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )

        input_username = form.name.data
        input_email = str(form.email.data).lower()
        input_message = form.message.data

        try:
            send_contact_validation_link(input_username, input_email, input_message)
        except Exception as e:
            app.logger.exception("Echec envoi email de validation contact")
            log_events.log_event(
                f"[400] Flask - Echec envoi email de validation contact: {e}",
                {"username": input_username, "email": input_email},
            )
            return render_template(
                "mail_not_sent.html",
                name=input_username,
                is_authenticated=current_user.is_authenticated,
            )

        log_events.log_event(
            "[200] Flask - Email de validation de contact envoyé.",
            {"username": input_username, "email": input_email},
        )
        return render_template(
            "contact_validation_sent.html",
            name=input_username,
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

        if not response_json.get('success'):
            flash("Echec vérification hCaptcha, essayez de nouveau.", "error")
            session.close()
            return render_template(
                "login.html",
                form=form,
                is_authenticated=current_user.is_authenticated,
            )

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
            if not user.is_active:
                session.close()
                flash(f"Compte {user} inactif. Pour l'activer, vous devez utiliser le lien renvoyé.")
                send_activation_link(user.email)
                logs_context = {"username": f"{username}", "email": f"{email}"}
                log_events.log_event("[301] Flask - Compte utilisateur inactif, echec connexion.", logs_context)
                return redirect(url_for("index"))
            login_user(user)
            flash(f"Vous nous avez manqué {user} 🫶")
            logs_context = {"username": f"{username}"}
            log_events.log_event("[200] Flask - Connexion à application.", logs_context)
            session.close()
            return redirect(url_for("index"))

        logs_context = {"username": f"{username}", "email": f"{email}"}
        log_events.log_event(
            "[400] Flask - Echec connexion à application. Mot de passe ou email invalide.",
            logs_context,
        )
        flash("Mot de passe ou email invalide.", "error")
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


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # Try to load the email from the token
        email = sengrid_tokens_serializer.loads(token, salt='email-confirmation', max_age=86400)  # 1 day expiry
    except Exception as e:
        flash("Le lien de confirmation n'est pas valide ou a expiré.")
        return redirect(url_for("index"))

    # Ensure user exists and then activate his account
    session = session_commands.get_a_database_session()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        session.close()
        logs_context = {
            "email": f"{email}",
        }
        log_events.log_event("[404] Flask - Utilisateur inconnu tente d'activer son compte", logs_context)
        flash("Le lien de confirmation n'est pas valide ou a expiré.", "error")
        return redirect(url_for("index"))
    user.is_active = True
    session.commit()
    logs_context = {
        "current_user": f"{user.username}",
    }
    log_events.log_event("[200] Flask - Compte activé.", logs_context)
    flash(f"Compte activé {user} 💪, vous pouvez maintenant vous connecter.")
    session.close()
    return redirect(url_for("index"))


def send_activation_link(email):
    # Create a token with email that expires in 24 hours
    token = sengrid_tokens_serializer.dumps(email, salt='email-confirmation')

    # Generate confirmation link
    confirm_url = url_for('confirm_email', token=token, _external=True)

    if os.getenv("SCOPE") == "production":
        message = Mail(
            from_email="no-reply@dummy-ops.dev",
            to_emails=email,
            subject="Dummy-ops books",
            # plain_text_content=f"Click here to confirm your registration: {confirm_url}"
            html_content=f"""
                <p>Click sur le lien pour confirmer l'inscription : <a href="{confirm_url}">valider l'inscription</a></p><br>
            """
        )

        # Send the email
        SENDGRID_API_KEY = get_secret("/run/secrets/SENDGRID_API_KEY")
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception:
            return {"status": "failure", "message": "Mail sending failed"}

    elif os.getenv("SCOPE") == "development":
        # We use smtplib and MailTrap
        mailtrap_user_name = os.getenv("MAILTRAP_USER_NAME")
        mailtrap_user_password = os.getenv("MAILTRAP_USER_PASSWORD")
        # Email configuration
        sender = "no-reply@dummy-ops.dev"
        receiver = "to@example.com"
        subject = "Dummy-ops books"

        msg = MIMEMultipart()
        msg['Subject'] = "Dummy-ops books"
        msg['To'] = receiver
        msg['From'] = sender

        html = f"""
        <html>
            <body>
                <p>Votre lien pour valider l'inscription:</p>
                <p><a href="{confirm_url}">Cliquez ici pour valider</a></p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))

        # Send the email
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
            server.starttls()
            server.login(mailtrap_user_name, mailtrap_user_password)
            # server.send_message(msg, sender, receiver)
            server.set_debuglevel(1)
            result = server.send_message(msg, sender, receiver)
            print("Scope development on log l'envoi:", result)


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
            if user_email.is_active:
                flash("Email existe déjà en base et compte actif", "error")
            else:
                flash("Compte inactif, lien d'activation renvoyé", "error")
                send_activation_link(email)
        elif form.password.data != form.password_check.data:
            flash("Mots de passe ne correspondent pas", "error")
        else:
            if not user:
                new_user = User(
                    username=username, hashed_password=hashed_password, email=email
                )
                session.add(new_user)
                session.commit()
                send_activation_link(email)
                flash(f"Bienvenue {new_user.username}, pour vous connecter utilisez le lien envoyé à {email}", "info")
                logs_context = {"username": f"{new_user.username}", "email": f"{email}"}
                session.close()
                log_events.log_event(
                    "[201] Flask - Création compte utilisateur en attente d'activation.", logs_context
                )
                return redirect(url_for("index"))
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
                    flash(
                        f"Bienvenue avant de pouvoir vous connecter, utilisez le lien envoyé à {username.email}", "info"
                    )
                    logs_context = {"username": f"{username}", "email": f"{email}"}
                    log_events.log_event(
                        "[201] Flask - Création compte utilisateur en attente d'activation.", logs_context
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


@app.route("/misc/")
def misc():
    """
    Description: the miscellaneous Flask route.
    """
    return redirect("https://dummy-sudoku-resolver-front.onrender.com")


@app.route("/moocs/")
def moocs():
    """
    Description: the moocs Flask route.
    """
    return render_template("moocs.html", is_authenticated=current_user.is_authenticated)


@app.route("/ops/")
def ops():
    """
    Description: the ops Flask route.
    """
    return render_template("ops.html", is_authenticated=current_user.is_authenticated)


@app.route("/status/")
def status_page():
    """
    Description: the status Flask route.
    """
    return redirect("https://status.dummy-ops.dev/")


@app.route("/mentions-legales/")
def mentions_legales():
    return render_template("mentions_legales.html", is_authenticated=current_user.is_authenticated)


@app.route("/politique-de-confidentialite/")
def politique_confidentialite():
    return render_template("politique_confidentialite.html", is_authenticated=current_user.is_authenticated)


@app.route("/cookies/")
def cookies():
    return render_template("cookies.html", is_authenticated=current_user.is_authenticated)


@app.route("/cgu/")
def cgu():
    return render_template("cgu.html", is_authenticated=current_user.is_authenticated)
