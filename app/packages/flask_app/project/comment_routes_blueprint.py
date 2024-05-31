""" The Comment blueprint routes """

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
from app.packages.database.models.models import Comment, Book
from . import forms

comment_routes_blueprint = Blueprint("comment_routes_blueprint", __name__)


@comment_routes_blueprint.route(
    "/comment/<int:comment_id>/delete/", methods=["GET", "POST"]
)
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
        return redirect(url_for("book_routes_blueprint.books"))
    session.close()
    return render_template(
        "delete_comment.html",
        form=form,
        comment_to_delete=comment_to_delete,
        is_authenticated=current_user.is_authenticated,
    )


@comment_routes_blueprint.route(
    "/comment/<int:comment_id>/update/", methods=["GET", "POST"]
)
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
        return redirect(url_for("book_routes_blueprint.books"))
    session.close()
    return render_template(
        "update_comment.html",
        form=edit_form,
        is_authenticated=current_user.is_authenticated,
    )
