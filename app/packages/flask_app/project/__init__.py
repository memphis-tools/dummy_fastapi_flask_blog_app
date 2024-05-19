""" The Flask app definition.Notice we do not use the app factory pattern """


import os
import base64
from io import BytesIO
import random
from functools import wraps
import matplotlib.pyplot as plt
from flask import (
    Flask,
    url_for,
    render_template,
    flash,
    abort,
    redirect,
    request,
)

from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_wtf import CSRFProtect
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from app.packages import handle_passwords, log_events, settings
from app.packages.database.commands import session_commands
from app.packages.database.models.models import Book, Comment, User, BookCategory, Starred
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
    session = session_commands.get_a_database_session()
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
    session = session_commands.get_a_database_session()
    category = session.get(BookCategory, id)
    session.close()
    return category


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
    for category in settings.BOOKS_CATEGORIES:
        color_index = get_random_color(colors_list)
        color = colors_list[color_index]
        colors.append(color)
        colors_list.remove(color)
    return colors


def create_books_categories_chart(total_books, categories_books_count_dict):
    """
    Description: build a matplotlib pie based on books categories.
    """
    labels = tuple(categories_books_count_dict.keys())
    sizes = []
    for value in categories_books_count_dict.values():
        sizes.append((value / total_books) * 100)
    colors = get_pie_colors()
    fig, ax = plt.subplots(figsize=(9, 6))
    explode_list = []
    [explode_list.append(0.1) for distance in range(0, len(labels))]
    explode = tuple(explode_list)
    ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        labels=labels,
        autopct="%1.1f%%",
        shadow=True,
    )
    ax.set_aspect("equal")
    fig.legend(labels)
    return fig


@app.route("/front/books/categories/stats/")
@login_required
def categories_stats():
    """
    Description: returns a book's categories pie chart.
    """
    total_books = 0
    categories_books_count_dict = {}
    session = session_commands.get_a_database_session()
    books_categories_list = session.query(BookCategory).all()
    for category in books_categories_list:
        category_id = (
            session.query(BookCategory).filter_by(title=f"{category}").first().id
        )
        books_count = (
            session.query(func.count(Book.category))
            .filter(Book.category == category_id)
            .all()[0]
        )
        if bool(books_count[0] > 0):
            categories_books_count_dict[f"{category}"] = books_count[0]
        total_books += books_count[0]
    session.close()
    fig = create_books_categories_chart(total_books, categories_books_count_dict)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"""
        <!DOCTYPE html>
        <html lang='en'>
            <head>
                <meta charset='utf-8' />
                <meta name='viewport' content='width=device-width, initial-scale=1, user-scaler=false' />
                <meta name='description' content='A blog Python's app.' />
                <meta name='author' content='dummy-ops' />
                <title>STATS</title>
                <link rel='icon' type='image/x-icon' href='/static/favicon.ico' />
                <!-- Google fonts-->
                <link rel='preconnect' href='https://fonts.googleapis.com'>
                <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
                <link href='https://fonts.googleapis.com/css2?family=Truculenta:opsz,wght@12..72,100..900&display=swap'
                 rel='stylesheet'>
                <!--  Boostrap css -->
                <link rel='stylesheet' href='/static/bootstrap.min.css'>
                <!-- Custom css -->
                <link rel='stylesheet' href='/static/styles.css'>
            </head>
            <body>
            <header>
            <!-- Navigation-->
            <nav class='navbar navbar-expand-lg navbar-dark fixed-top bg-dark'>
              <div class='container-fluid navbar-container'>
                <a class='dummy_logo navbar-brand' href='/front/home/'>DUMMY-OPS</a>
                <button class='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#navbarCollapse'
                aria-controls='navbarCollapse' aria-expanded='false' aria-label='Toggle navigation'>
                    <span class='navbar-toggler-icon'></span>
                </button>
                <div class='collapse navbar-collapse' id='navbarCollapse'></div>
              </div>
            </nav>
            </header>
                <section>
                <div class='container'>
                    <div class='section_intro'></div>
                    <h1>DUMMY BLOG - LES CATEGORIES</h1>
                    <div class='home-stats-container'>
                          <div class='stat-post'>
                              <p class='stat-title'></p>
                              <img src='data:image/png;base64,{data}'/>
                          </div>
                          <hr />
                    </div>
                </div>
                </section>
            <!-- Footer-->
              <footer class='border-top'>
                  <div class='footer-container'>
                      <div class='d-flex flex-column justify-content-center'>
                        <div class='social-networks'>
                            <ul>
                             <li>
                               <a class='d-flex' href='https://gitlab.com/memphis-tools/dummy_fastapi_flask_blog_app'
                               target='_blank'>
                                   <span class='fa-stack fa-lg'>
                                       <i class='fas fa-circle fa-stack-2x'></i>
                                       <i class='fab fa-gitlab fa-stack-1x fa-inverse'></i>
                                   </span>
                             </li>
                             <li>
                               </a>
                                 <a class='d-flex' href='https://github.com/memphis-tools/dummy_fastapi_flask_blog_app'
                                 target='_blank'>
                                     <span class='fa-stack fa-lg'>
                                         <i class='fas fa-circle fa-stack-2x'></i>
                                         <i class='fab fa-github fa-stack-1x fa-inverse'></i>
                                     </span>
                                 </a>
                             </li>
                            </ul>
                        </div>
                        <div class='text-center' id='footer_date'></div>
                        <div class='provider-logo'>
                          <a href='https://www.digitalocean.com/?refcode=4f541e02cfe5&utm_campaign=Referral_Invite
                          &utm_medium=Referral_Program&utm_source=badge'>
                          <img src='https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%202.svg'
                          alt='DigitalOcean Referral Badge' /></a>
                        </div>
                      </div>
                  </div>
              </footer>
              <script src='/static/scripts.js'></script>
              <script src='/static/all.js'></script>
              <script src='/static/bootstrap.bundle.min.js'></script>
            </body>
        </html>
    """


def create_users_chart(total_books, users_books_count_dict):
    """
    Description: build a matplotlib pie based on users publications.
    """
    labels = tuple(users_books_count_dict.keys())
    sizes = []
    for value in users_books_count_dict.values():
        sizes.append((value / total_books) * 100)
    colors = get_pie_colors()
    fig, ax = plt.subplots(figsize=(9, 6))
    explode_list = []
    [explode_list.append(0.1) for distance in range(0, len(labels))]
    explode = tuple(explode_list)
    ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        labels=labels,
        autopct="%1.1f%%",
        shadow=True,
    )
    ax.set_aspect("equal")
    fig.legend(labels)
    return fig


@app.route("/front/books/users/stats/")
@login_required
def users_stats():
    """
    Description: returns an user's publications pie chart.
    """
    total_books = 0
    users_books_count_dict = {}
    session = session_commands.get_a_database_session()
    users_list = session.query(User).all()
    for user in users_list:
        books_count = (
            session.query(func.count(Book.category))
            .filter(Book.user_id == user.id)
            .all()[0]
        )
        if bool(books_count[0] > 0):
            users_books_count_dict[f"{user}"] = books_count[0]
        total_books += books_count[0]
    session.close()
    fig = create_users_chart(total_books, users_books_count_dict)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"""
        <!DOCTYPE html>
        <html lang='en'>
            <head>
                <meta charset='utf-8' />
                <meta name='viewport' content='width=device-width, initial-scale=1, user-scaler=false' />
                <meta name='description' content='A blog Python's app.' />
                <meta name='author' content='dummy-ops' />
                <title>STATS</title>
                <link rel='icon' type='image/x-icon' href='/static/favicon.ico' />
                <!-- Google fonts-->
                <link rel='preconnect' href='https://fonts.googleapis.com'>
                <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
                <link href='https://fonts.googleapis.com/css2?family=Truculenta:opsz,wght@12..72,100..900&display=swap'
                rel='stylesheet'>
                <!--  Boostrap css -->
                <link rel='stylesheet' href='/static/bootstrap.min.css'>
                <!-- Custom css -->
                <link rel='stylesheet' href='/static/styles.css'>
            </head>
            <body>
            <header>
            <!-- Navigation-->
            <nav class='navbar navbar-expand-lg navbar-dark fixed-top bg-dark'>
              <div class='container-fluid navbar-container'>
                <a class='dummy_logo navbar-brand' href='/front/home/'>DUMMY-OPS</a>
                <button class='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#navbarCollapse'
                aria-controls='navbarCollapse' aria-expanded='false' aria-label='Toggle navigation'>
                    <span class='navbar-toggler-icon'></span>
                </button>
                <div class='collapse navbar-collapse' id='navbarCollapse'></div>
              </div>
            </nav>
            </header>
                <section>
                <div class='container'>
                    <div class='section_intro'></div>
                    <h1>DUMMY BLOG - LES UTILISATEURS</h1>
                    <div class='home-stats-container'>
                          <div class='stat-post'>
                              <p class='stat-title'></p>
                              <img src='data:image/png;base64,{data}'/>
                          </div>
                          <hr />
                    </div>
                </div>
                </section>
            <!-- Footer-->
              <footer class='border-top'>
                  <div class='footer-container'>
                      <div class='d-flex flex-column justify-content-center'>
                        <div class='social-networks'>
                            <ul>
                                <li>
                                  <a class='d-flex' href='https://gitlab.com/memphis-tools/dummy_fastapi_flask_blog_app'
                                  target='_blank'>
                                      <span class='fa-stack fa-lg'>
                                          <i class='fas fa-circle fa-stack-2x'></i>
                                          <i class='fab fa-gitlab fa-stack-1x fa-inverse'></i>
                                      </span>
                                </li>
                                <li>
                                  </a>
                                    <a class='d-flex' href='https://github.com/memphis-tools/dummy_fastapi_flask_blog_app'
                                    target='_blank'>
                                        <span class='fa-stack fa-lg'>
                                            <i class='fas fa-circle fa-stack-2x'></i>
                                            <i class='fab fa-github fa-stack-1x fa-inverse'></i>
                                        </span>
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div class='text-center' id='footer_date'></div>
                        <div class='provider-logo'>
                          <a href='https://www.digitalocean.com/?refcode=4f541e02cfe5&utm_campaign=Referral_Invite
                          &utm_medium=Referral_Program&utm_source=badge'>
                          <img src='https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%202.svg'
                          alt='DigitalOcean Referral Badge' /></a>
                        </div>
                      </div>
                  </div>
              </footer>
              <script src='/static/scripts.js'></script>
              <script src='/static/all.js'></script>
              <script src='/static/bootstrap.bundle.min.js'></script>
            </body>
        </html>
    """


@app.route("/front/stats/")
@login_required
def stats():
    """
    Description: the stats Flask route.
    """
    return render_template("stats.html", is_authenticated=current_user.is_authenticated)


@app.route("/front")
@app.route("/front/home/")
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
    first_books = session.query(Book).filter(
        Book.id.in_(random_ids)
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    ).all()
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
    session = session_commands.get_a_database_session()
    books = session.query(Book).order_by(
        Book.id
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    ).all()
    total_books = len(books)
    # Get the 'page' query parameter from the URL
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    # Calculate the start and end indices of the items to display
    start = (page - 1) * per_page
    end = start + per_page
    # Get the subset of items for the current page
    items = books[start:end]
    # Calculate the total number of pages
    total_pages = len(books) // per_page + (1 if len(books) % per_page > 0 else 0)
    session.close()
    return render_template(
        "books.html",
        books=items,
        page=page,
        total_books=total_books,
        per_page=per_page,
        total_pages=total_pages,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/book/<int:book_id>/", methods=["GET", "POST"])
@login_required
def book(book_id):
    """
    Description: the book Flask route.
    """
    session = session_commands.get_a_database_session()
    delete_book_form = forms.DeleteInstanceForm()
    form = forms.CommentForm()
    book = session.query(Book).filter(
        Book.id == book_id
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    ).first()

    comments = session.query(Comment).filter_by(book_id=book.id).all()

    user_starred_books_id_list = session.query(Starred).filter(
        Starred.user_id == current_user.id
    ).with_entities(
        Starred.book_id
    ).all()

    logs_context = {
        "current_user": f"{current_user.username}",
        "book_id": book_id,
        "book_title": book.title,
    }
    log_events.log_event("[+] Flask - Consultation livre.", logs_context)

    if request.method == "POST":
        if form.validate_on_submit():
            new_comment = Comment(
                text=form.comment_text.data, author_id=current_user.id, book_id=book.id
            )
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": book.title,
            }
            log_events.log_event("[+] Flask - Ajout commentaire.", logs_context)
            session.add(new_comment)
            session.commit()
        session.close()
        return redirect(url_for("books"))
    session.close()
    return render_template(
        "book.html",
        book=book,
        user_starred_books_id_list=user_starred_books_id_list,
        form=form,
        delete_book_form=delete_book_form,
        comments=comments,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/users/<int:user_id>/starred/")
@login_required
def user_starred(user_id):
    """
    Description: a user's book starred Flask route.
    As soon as an user is authenticated he should be able to consult his starred books
    and those from any existing users.
    """
    session = session_commands.get_a_database_session()
    user = session.query(User).filter(
        User.id == user_id
    ).first()
    if not user:
        flash(f"Utilisateur id {user_id} inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    user_starred_books = session.query(
        Book
    ).join(
        Starred
    ).filter(
        Book.id == Starred.book_id
    ).filter(
        Starred.user_id == user_id
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    ).all()
    books = user_starred_books
    session.close()
    return render_template(
        "books_starred.html", books=books, user=user, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/users/<int:user_id>/books/<int:book_id>/starred/delete/", methods=["GET", "POST"])
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
    starred_book_to_delete = session.query(Starred).filter(
        Starred.book_id == book_id
    ).filter(
        Starred.user_id == user_id
    ).first()
    if not starred_book_to_delete:
        flash("Favori inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    if not user_id == current_user.id:
        flash("Vous ne pouvez supprimer que vos favoris", "error")
        session.close()
        return redirect(url_for("index"))
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "starred_book_deleted": starred_book_to_delete,
        }
        log_events.log_event("[+] Flask - Suppression favori.", logs_context)
        session.delete(starred_book_to_delete)
        session.commit()
        flash("Favori supprimé", "info")
        session.close()
        return redirect(url_for(
            "book",
            book_id=starred_book_to_delete.id,
            is_authenticated=current_user.is_authenticated,
        ))
    return render_template(
        "delete_starred_book.html",
        form=form,
        book_to_delete=starred_book_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/users/<int:user_id>/books/<int:book_id>/starred/add/", methods=["GET", "POST"])
@login_required
def add_starred_book(user_id, book_id):
    """
    Description: the remove starred book Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.AddInstanceForm()
    starred_book_to_add = session.query(Starred).filter(
        Starred.book_id == book_id
    ).filter(
        Starred.user_id == user_id
    ).first()

    if starred_book_to_add:
        flash("Vous avez deja ce livre en favori", "error")
        session.close()
        return redirect(url_for("index", is_authenticated=current_user.is_authenticated,))

    if not user_id == current_user.id:
        flash("Vous ne pouvez ajouter que vos favoris", "error")
        session.close()
        return redirect(url_for("index"))

    if form.validate_on_submit():
        book = session.query(Book).filter(
            Book.id == book_id
        ).first()
        if not book:
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
        log_events.log_event("[+] Flask - Ajout favori.", logs_context)
        session.add(new_starred_book)
        session.commit()
        session.close()
        flash("Livre en favori", "info")
        return redirect(url_for(
            "book",
            book_id=book_id,
            is_authenticated=current_user.is_authenticated,
        ))
    session.close()
    return render_template(
        "add_starred_book.html",
        form=form,
        book_to_add=starred_book_to_add,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/books/categories/")
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


@app.route("/front/books/categories/<int:category_id>/")
def category_books(category_id):
    """
    Description: the books from a category Flask route.
    """
    session = session_commands.get_a_database_session()
    category = session.query(BookCategory).filter(BookCategory.id == category_id).first()
    if not category:
        flash(f"Categorie id {category_id} inexistante", "error")
        session.close()
        return redirect(url_for("index"))
    category_books_query = session.query(Book).filter(
        Book.category.in_(
            [
                category_id,
            ]
        )
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    )
    books = category_books_query.all()
    session.close()
    return render_template(
        "category_books.html",
        category=category,
        books=books,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/user/<int:user_id>/books/")
@login_required
def user_books(user_id):
    """
    Description: the user's book Flask route.
    """
    if not current_user.is_authenticated:
        flash("Acces page interdit aux utilisateurs non connectés.", "error")
        return redirect(url_for("register"))
    session = session_commands.get_a_database_session()
    user = session.get(User, user_id)
    if not user:
        flash(f"Utilisateur id {user_id} inexistant", "error")
        session.close()
        return redirect(url_for("index"))
    books_query = session.query(Book).filter(
        Book.user_id.in_(
            [
                user_id,
            ]
        )
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    )
    books = books_query.all()
    session.close()
    if current_user.id == user_id:
        return render_template(
            "user_books.html",
            books=books,
            user_name=user.username,
            is_authenticated=current_user.is_authenticated,
        )
    else:
        return render_template(
            "user_any_books.html",
            books=books,
            user_name=user.username,
            is_authenticated=current_user.is_authenticated,
        )


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


@app.route("/front/books/add/", methods=["GET", "POST"])
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
            if os.getenv("SCOPE") == "production":
                book_picture.save(
                    os.path.join(app.instance_path, "staticfiles", filename)
                )
            else:
                new_book.book_picture_name = "dummy_blank_book.png"
            session.add(new_book)
            session.commit()
            session.refresh(new_book)
            user = session.get(User, new_book.user_id)
            session.commit()
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": new_book.title,
            }
            log_events.log_event("[+] Flask - Ajout livre.", logs_context)
            session.close()
            return redirect(url_for("books"))
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


@app.route("/front/login/", methods=["GET", "POST"])
def login():
    """
    Description: the login Flask route.
    Ensure the email is well formed (in database).
    """
    form = forms.LoginForm()
    if form.validate_on_submit():
        session = session_commands.get_a_database_session()
        email = str(form.email.data).lower()
        username = str(form.login.data).lower()
        password = form.password.data
        user = session.query(User).filter_by(username=username).first()
        if not user or user.email != email:
            logs_context = {"username": f"{username}", "email": f"{email}"}
            log_events.log_event(
                "[+] Flask - Echec connexion à application.", logs_context
            )
            flash("Identifiants invalides", "error")
        else:
            if check_password_hash(user.hashed_password, password):
                login_user(user)
                flash(f"Vous nous avez manqué {user} 🫶")
                logs_context = {"username": f"{username}"}
                log_events.log_event(
                    "[+] Flask - Connexion à application.", logs_context
                )
                session.close()
                return redirect(url_for("index"))
            else:
                logs_context = {"username": f"{username}", "email": f"{email}"}
                log_events.log_event(
                    "[+] Flask - Echec connexion à application. Mot de passe invalide.",
                    logs_context,
                )
                flash("Mot de passe invalide", "error")
        session.close()
    return render_template(
        "login.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/users/password/", methods=["GET", "POST"])
@login_required
def update_password():
    """
    Description: the update user password Flask route.
    """
    form = forms.UpdateUserPasswordForm()
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
            flash(f"Mot de passe mis a jour {current_user} 💪")
            session.close()
            return redirect(url_for("index"))
    return render_template(
        "update_password.html",
        form=form,
        is_authenticated=current_user.is_authenticated,
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
    session = session_commands.get_a_database_session()
    form = forms.RegisterForm()
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
                flash(f"Bienvenue {username} vous pouvez vous connecter", "info")
                logs_context = {"username": f"{username}", "email": f"{email}"}
                log_events.log_event(
                    "[+] Flask - Création compte utilisateur.", logs_context
                )
                session.close()
                return redirect(url_for("login"))
            else:
                flash("Nom utilisateur existe deja, veuillez le modifier", "error")
    session.close()
    return render_template(
        "register.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/users/add/", methods=["GET", "POST"])
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
                    "[+] Flask - Création compte utilisateur par admin.", logs_context
                )
                session.close()
                return redirect(url_for("login"))
            else:
                flash("Nom utilisateur existe deja, veuillez le modifier", "error")
    session.close()
    return render_template(
        "add_user.html", form=form, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/comment/<int:comment_id>/update/", methods=["GET", "POST"])
@login_required
def update_comment(comment_id):
    """
    Description: the update comment Flask route.
    """
    session = session_commands.get_a_database_session()
    comment = session.get(Comment, comment_id)
    edit_form = forms.UpdateCommentForm(
        comment_text=comment.text,
    )
    if current_user.id != comment.author_id and current_user.role != "admin":
        session.close()
        return abort(403)
    if edit_form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "old_comment": comment.text,
            "new_comment": edit_form.comment_text.data,
        }
        log_events.log_event("[+] Flask - Mise à jour commentaire.", logs_context)
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
    session = session_commands.get_a_database_session()
    book = session.query(Book).filter(
        Book.id.in_([book_id])
    ).options(
        joinedload(Book.book_comments)
    ).options(
        joinedload(Book.starred)
    ).first()
    if book:
        if current_user.id != book.user_id and current_user.role != "admin":
            session.close()
            return abort(403)
        book_picture_filename = book.book_picture_name
        books_categories_query = session.query(BookCategory).all()
        books_categories = [(i.id, i.title) for i in books_categories_query]
        edit_form = forms.UpdateBookForm(
            books_categories=books_categories,
            book=book,
        )
        if edit_form.validate_on_submit():
            form = request.form.to_dict()
            form_file = request.files.to_dict
            if "title" in form:
                title = form["title"]
            else:
                title = book.title
            if "summary" in form:
                summary = form["summary"]
            else:
                summary = book.summary
            if "content" in form:
                content = form["content"]
            else:
                content = book.content
            if "author" in form:
                author = form["author"]
            else:
                author = book.author
            if "year_of_publication" in form:
                year_of_publication = int(form["year_of_publication"])
            else:
                year_of_publication = book.year_of_publication
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
                book_picture = form_file["photo"]
            except Exception:
                book_picture = None
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
                if os.getenv("SCOPE") == "production":
                    book_picture.save(
                        os.path.join(app.instance_path, "staticfiles", filename)
                    )
                    try:
                        os.remove(
                            f"{app.instance_path}staticfiles/{book_picture_filename}"
                        )
                    except FileNotFoundError:
                        pass
                else:
                    updated_book.book_picture_name = "dummy_blank_book.png"

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
                return redirect(url_for("book", book_id=book_id))
            else:
                flash(book_is_valid, "error")
                session.close()
                return render_template(
                    "update_book.html",
                    form=edit_form,
                    is_authenticated=current_user.is_authenticated,
                )
        return render_template(
            "update_book.html",
            form=edit_form,
            is_authenticated=current_user.is_authenticated,
        )
    else:
        flash("Livre non trouvé", "error")
        return redirect(url_for("books"))
    session.close()


@app.route("/front/users/", methods=["GET"])
@login_required
@admin_only
def users():
    """
    Description: the users app Flask route.
    """
    session = session_commands.get_a_database_session()
    # remember that user with id 1 is the application admin (wr remove it from dataset)
    users = session.query(User).all()[1:]
    session.close()
    return render_template(
        "users.html", users=users, is_authenticated=current_user.is_authenticated
    )


@app.route("/front/categories/", methods=["GET"])
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


@app.route("/front/book/categories/add/", methods=["GET", "POST"])
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
        return redirect(url_for("manage_books_categories"))
    return render_template(
        "add_book_category.html",
        form=form,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/user/<int:user_id>/delete/", methods=["GET", "POST"])
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
        session.close()
        flash("Le compte admin ne peut pas etre supprime", "error")
        return abort(403)
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "user_to_delete": user_to_delete.username,
        }
        log_events.log_event("[+] Flask - Suppression utilisateur.", logs_context)
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


@app.route("/front/book/categories/<int:category_id>/delete/", methods=["GET", "POST"])
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
        return redirect(url_for("manage_books_categories"))
    return render_template(
        "delete_book_category.html",
        category_to_delete=category_to_delete,
        form=form,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/book/categories/<int:category_id>/update/", methods=["GET", "POST"])
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
            return redirect(url_for("manage_books_categories"))
        else:
            flash(book_category_is_valid, "error")
            session.close()
            return redirect(url_for("index"))
        return redirect(url_for("manage_books_categories"))
    return render_template(
        "update_book_category.html",
        category_to_update=category_to_update,
        form=edit_form,
        is_authenticated=current_user.is_authenticated,
    )


@app.route("/front/book//<int:book_id>/delete/", methods=["GET", "POST"])
@login_required
def delete_book(book_id):
    """
    Description: the delete book Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    book_to_delete = session.get(Book, book_id)
    user = session.get(User, book_to_delete.user_id)
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
        os.remove(f"{app.instance_path}staticfiles/{book_picture_name}")
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book_to_delete.title,
        }
        log_events.log_event("[+] Flask - Suppression livre.", logs_context)
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
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    comment_to_delete = session.get(Comment, comment_id)
    book = session.get(Book, comment_to_delete.book_id)
    if current_user.id != comment_to_delete.author_id and current_user.role != "admin":
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book.title,
            "comment": comment_to_delete.text,
        }
        log_events.log_event(
            "[+] Flask - Suppression commentaire refusée.", logs_context
        )
        flash("Seul l'auteur du commentaire peut le supprimer", "error")
        session.close()
        return abort(403)
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book.title,
            "comment": comment_to_delete.text,
        }
        log_events.log_event("[+] Flask - Suppression commentaire.", logs_context)
        session.delete(comment_to_delete)
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


@app.route("/front/ops/")
def ops():
    """
    Description: the ops Flask route.
    """
    return render_template("ops.html", is_authenticated=current_user.is_authenticated)


@app.route("/front/moocs/")
def moocs():
    """
    Description: the moocs Flask route.
    """
    return render_template("moocs.html", is_authenticated=current_user.is_authenticated)
