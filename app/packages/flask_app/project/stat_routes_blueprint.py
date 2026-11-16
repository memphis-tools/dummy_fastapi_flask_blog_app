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

stat_routes_blueprint = Blueprint("stat_routes_blueprint", __name__)

PIE_CHART_COLORS = [
    "#2f5d8a",
    "#4c9f70",
    "#e0a458",
    "#c65d57",
    "#7b6da6",
    "#3e8e9e",
    "#d98e4a",
    "#8a8f98",
    "#5b8c5a",
    "#b565a7",
    "#6c7a89",
    "#a8763e",
]


@stat_routes_blueprint.route("/stats/")
@login_required
def stats():
    """
    Description: the stats Flask route.
    """
    return render_template("stats.html", is_authenticated=current_user.is_authenticated)


def fig_to_base64(fig):
    """
    Description: render a matplotlib figure to a base64 png string.
    """
    buf = BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=200,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
    return base64.b64encode(buf.getbuffer()).decode("ascii")


def _stats_page(heading, data):
    """
    Description: build the responsive stats page embedding a base64 chart.
    """
    return f"""
        <!DOCTYPE html>
        <html lang='en'>
            <head>
                <meta charset='utf-8' />
                <meta name='viewport' content='width=device-width, initial-scale=1' />
                <meta name='description' content='Blog stats.' />
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
                <!-- Responsive chart css -->
                <style>
                    .stat-chart {{
                        max-width: 760px;
                        margin: 0 auto;
                        padding: 0 12px;
                    }}
                    .stat-chart img {{
                        display: block;
                        width: 100%;
                        height: auto;
                    }}
                    h1 {{
                        text-align: center;
                        font-size: clamp(1.4rem, 4vw, 2.2rem);
                        overflow-wrap: break-word;
                    }}
                </style>
                <!-- Google AdSense -->
                <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?
                client=ca-pub-8024784230098804" crossorigin="anonymous"></script>
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
                    <h1>{heading}</h1>
                    <div class='home-stats-container'>
                          <div class='stat-post stat-chart'>
                              <p class='stat-title'></p>
                              <img src='data:image/png;base64,{data}' alt='{heading}'/>
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


def _contrast_text_color(hex_color):
    """
    Description: return a readable text color (dark or white) for a hex background.
    """
    hex_color = hex_color.lstrip("#")
    red, green, blue = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
    return "#212529" if luminance > 0.6 else "#ffffff"


def _build_professional_pie_chart(title, subtitle, total, data_dict):
    """
    Description: build a professional donut chart from a {label: count} dict.
    """
    labels = list(data_dict.keys())
    counts = list(data_dict.values())
    sizes = (
        [(value / total) * 100 for value in counts]
        if total
        else [0.0] * len(counts)
    )
    colors = [
        PIE_CHART_COLORS[index % len(PIE_CHART_COLORS)]
        for index in range(len(labels))
    ]
    explode = [0.0] * len(labels)
    if sizes:
        explode[sizes.index(max(sizes))] = 0.05
    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    wedges, _labels, autotexts = ax.pie(
        sizes,
        explode=explode,
        colors=colors,
        startangle=90,
        counterclock=False,
        autopct=lambda pct: f"{pct:.1f} %",
        pctdistance=0.79,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 10, "fontweight": "bold"},
    )
    for autotext, color in zip(autotexts, colors):
        autotext.set_color(_contrast_text_color(color))
    fig.suptitle(title, fontsize=16, fontweight="bold", color="#212529", y=0.98)
    ax.set_title(subtitle, fontsize=10, color="#6c757d", pad=12)
    ax.text(
        0,
        0,
        f"{total}\nlivres",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="#212529",
    )
    legend_labels = [
        f"{label} : {count} ({(count / total) * 100:.1f} %)" if total else str(label)
        for label, count in zip(labels, counts)
    ]
    fig.legend(
        wedges,
        legend_labels,
        title="Légende",
        title_fontsize=11,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        fontsize=10,
    )
    fig.text(
        0.99,
        0.01,
        "Source : DUMMY-OPS",
        ha="right",
        va="bottom",
        fontsize=8,
        color="#adb5bd",
    )
    ax.set_aspect("equal")
    return fig


def create_books_categories_chart(total_books, categories_books_count_dict):
    """
    Description: build a matplotlib pie based on books categories.
    """
    return _build_professional_pie_chart(
        "Répartition des livres par catégorie",
        "Nombre de livres et part en pourcentage",
        total_books,
        categories_books_count_dict,
    )


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
    data = fig_to_base64(fig)
    return _stats_page("DUMMY OPS - LES CATEGORIES", data)


def create_users_chart(total_books, users_books_count_dict):
    """
    Description: build a matplotlib pie based on users publications.
    """
    return _build_professional_pie_chart(
        "Répartition des publications par utilisateur",
        "Nombre de publications et part en pourcentage",
        total_books,
        users_books_count_dict,
    )


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
    data = fig_to_base64(fig)
    return _stats_page("DUMMY OPS - LES UTILISATEURS", data)