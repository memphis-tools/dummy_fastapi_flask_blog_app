""" The Stat blueprint routes """

import base64
from io import BytesIO
import matplotlib.pyplot as plt
from flask import (
    Blueprint,
    render_template,
)
from flask_login import (
    current_user,
    login_required,
)
from sqlalchemy import func

try:
    from database.commands import session_commands
    from database.models.models import Book, BookCategory, User
except ModuleNotFoundError:
    from app.packages.database.commands import session_commands
    from app.packages.database.models.models import Book, BookCategory, User
from .shared_functions_and_decorators import get_pie_colors

stat_routes_blueprint = Blueprint("stat_routes_blueprint", __name__)


@stat_routes_blueprint.route("/stats/")
@login_required
def stats():
    """
    Description: the stats Flask route.
    """
    return render_template("stats.html", is_authenticated=current_user.is_authenticated)


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


@stat_routes_blueprint.route("/books/categories/stats/")
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
                <link rel='stylesheet' href='/static/css/bootstrap.min.css'>
                <!-- Custom css -->
                <link rel='stylesheet' href='/static/css/styles.css'>
            </head>
            <body>
            <header>
            <!-- Navigation-->
            <nav class='navbar navbar-expand-lg navbar-dark fixed-top bg-dark'>
              <div class='container-fluid navbar-container'>
                <a class='dummy_logo navbar-brand' href='/home/'>DUMMY-OPS</a>
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
              <script src='/static/js/scripts.js'></script>
              <script src='/static/js/all.js'></script>
              <script src='/static/js/bootstrap.bundle.min.js'></script>
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


@stat_routes_blueprint.route("/books/users/stats/")
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
                <link rel='stylesheet' href='/static/css/bootstrap.min.css'>
                <!-- Custom css -->
                <link rel='stylesheet' href='/static/css/styles.css'>
            </head>
            <body>
            <header>
            <!-- Navigation-->
            <nav class='navbar navbar-expand-lg navbar-dark fixed-top bg-dark'>
              <div class='container-fluid navbar-container'>
                <a class='dummy_logo navbar-brand' href='/home/'>DUMMY-OPS</a>
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
              <script src='/static/js/scripts.js'></script>
              <script src='/static/js/all.js'></script>
              <script src='/static/js/bootstrap.bundle.min.js'></script>
            </body>
        </html>
    """
