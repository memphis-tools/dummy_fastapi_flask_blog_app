""" The Quote blueprint routes """

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
from app.packages import log_events
from app.packages.database.commands import session_commands
from app.packages.database.models.models import Quote
from . import forms
from .shared_functions_and_decorators import admin_only


quote_routes_blueprint = Blueprint("quote_routes_blueprint", __name__)


@quote_routes_blueprint.route("/quotes/", methods=["GET"])
@login_required
@admin_only
def view_quotes():
    """
    Description: the quotes Flask route.
    """
    session = session_commands.get_a_database_session()
    quotes = session.query(Quote).all()
    session.close()
    return render_template(
        "view_quotes.html",
        quotes=quotes,
        is_authenticated=current_user.is_authenticated,
    )


@quote_routes_blueprint.route("/quotes/<int:quote_id>/", methods=["GET"])
@login_required
@admin_only
def view_quote(quote_id):
    """
    Description: the a quote Flask route.
    """
    session = session_commands.get_a_database_session()
    quote_to_view = session.get(Quote, quote_id)
    session.close()
    if not quote_to_view:
        session.close()
        flash("Citation inconnue", "error")
        return abort(404)
    return render_template(
        "view_quote.html",
        quote=quote_to_view,
        is_authenticated=current_user.is_authenticated,
    )


@quote_routes_blueprint.route("/quotes/add/", methods=["GET", "POST"])
@login_required
@admin_only
def add_quote():
    """
    Description: the add quote Flask route.
    """
    form = forms.CreateQuoteForm()
    if form.validate_on_submit():
        session = session_commands.get_a_database_session()
        author = str(form.author.data).lower()
        book_title = str(form.book_title.data).lower()
        quote = str(form.quote.data).lower()
        new_quote = Quote(author=author, book_title=book_title, quote=quote)
        session.add(new_quote)
        session.commit()
        flash(f"Ajout citation {author} {book_title} faite", "info")
        logs_context = {
            "author": f"{author}",
            "book_title": f"{book_title}",
            "quote": f"{quote}",
        }
        log_events.log_event("[+] Flask - Ajout citation par admin.", logs_context)
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))
    return render_template(
        "add_quote.html", form=form, is_authenticated=current_user.is_authenticated
    )


@quote_routes_blueprint.route(
    "/quotes/<int:quote_id>/delete/", methods=["GET", "POST"]
)
@login_required
@admin_only
def delete_quote(quote_id):
    """
    Description: the delete quote Flask route.
    """
    session = session_commands.get_a_database_session()
    form = forms.DeleteInstanceForm()
    quote_to_delete = session.get(Quote, quote_id)
    if not quote_to_delete:
        session.close()
        flash("Citation inconnue", "error")
        return abort(404)
    if form.validate_on_submit():
        logs_context = {
            "current_user": f"{current_user.username}",
            "quote_to_delete": quote_to_delete.author,
            "book_title": quote_to_delete.book_title,
        }
        log_events.log_event("[+] Flask - Suppression citation.", logs_context)
        session.delete(quote_to_delete)
        session.commit()
        session.close()
        return redirect(url_for("book_routes_blueprint.books"))
    session.close()
    return render_template(
        "delete_quote.html",
        form=form,
        quote=quote_to_delete,
        is_authenticated=current_user.is_authenticated,
    )
