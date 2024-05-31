"""The FastAPI routes for comments"""

from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.packages import log_events
from app.packages.database.commands import database_crud_commands
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    UserModel,
    NewCommentModel,
    UpdateCommentModel,
)
from ..dependencies import get_current_active_user, session

router = APIRouter()


@router.get("/api/v1/books/comments/all/", tags=["COMMENTS"])
async def view_comments(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_comments return a list of comments. Each comment is a dictionnary
    """
    comments = database_crud_commands.view_all_instances(session, models.Comment)
    return comments


@router.get("/api/v1/books/comments/{comment_id}/", tags=["COMMENTS"])
async def view_comment(
    comment_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_comment return a comment.
    """
    comment = database_crud_commands.get_instance(session, models.Comment, comment_id)
    return comment


@router.post("/api/v1/books/comments/", tags=["COMMENTS"])
async def add_comment(
    comment: NewCommentModel,
    book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    add a comment.
    """
    updated_book = database_crud_commands.get_instance(session, models.Book, book_id)
    new_comment = models.Comment(
        text=comment.text, book_id=book_id, author_id=current_user.id
    )
    if updated_book:
        session.add(new_comment)
        session.commit()
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": updated_book.title,
        }
        log_events.log_event("[+] FastAPI - Ajout commentaire.", logs_context)
        return new_comment

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Livre avec id {book_id} inexistant.",
    )


@router.put("/api/v1/books/comments/{comment_id}/", tags=["COMMENTS"])
async def update_comment(
    comment_id: int,
    comment_updated: UpdateCommentModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    full update of a comment instance.
    """
    comment = database_crud_commands.get_instance(session, models.Comment, comment_id)
    if comment:
        if current_user.id == comment.author_id or current_user.username == "admin":
            logs_context = {
                "current_user": f"{current_user.username}",
                "old_comment": comment.text,
                "new_comment": comment_updated.text,
            }
            log_events.log_event("[+] FastAPI - Mise à jour commentaire.", logs_context)
            if comment_updated.text is not None:
                comment.text = comment_updated.text
            session.query(models.Comment).where(models.Comment.id == comment_id).update(
                comment.get_json_for_update()
            )
            session.commit()
            session.refresh(comment)
            return comment
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent mettre à jour un commentaire",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Commentaire avec id {comment_id} inexistant.",
    )


@router.get("/api/v1/books/{book_id}/comments/", tags=["COMMENTS"])
async def view_book_comments(
    book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_book_comments returns a book's comments.
    """
    book = database_crud_commands.get_instance(session, models.Book, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livre n'existe pas."
        )
    comments = (
        session.query(models.Comment).where(models.Comment.book_id == book_id).all()
    )
    return comments


@router.delete("/api/v1/books/{book_id}/comments/{comment_id}/", tags=["COMMENTS"])
async def delete_comment(
    comment_id: int,
    book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    delete_comment allows to delete a comment base on id
    """
    updated_book = database_crud_commands.get_instance(session, models.Book, book_id)
    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Livre n'existe pas."
        )
    comment = database_crud_commands.get_instance(session, models.Comment, comment_id)
    if comment:
        if comment.book_id != book_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Commentaire non rattaché au livre.",
            )
        if current_user.id == comment.author_id:
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": updated_book.title,
                "comment": comment.text,
            }
            log_events.log_event("[+] FastAPI - Suppression commentaire.", logs_context)
            session.delete(comment)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"Commentaire avec id {comment_id} supprimé",
            )
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": updated_book.title,
            "comment": comment.text,
        }
        log_events.log_event(
            "[+] FastAPI - Suppression commentaire refusée.", logs_context
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent supprimer son commentaire",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Commentaire avec id {comment_id} inexistant.",
    )
