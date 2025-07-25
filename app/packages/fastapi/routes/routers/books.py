"""The FastAPI routes for books"""

import os
from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from celery import Celery

try:
    import log_events
    from database.commands import database_crud_commands, session_commands
    from database.models import models
    from app.fastapi.models.fastapi_models import (
        UserModel,
        NewBookModel,
        UpdateBookModel,
    )
    from utils import get_secret
except ModuleNotFoundError:
    from app.packages import log_events
    from app.packages.database.commands import database_crud_commands, session_commands
    from app.packages.database.models import models
    from app.packages.fastapi.models.fastapi_models import (
        UserModel,
        NewBookModel,
        UpdateBookModel,
    )
    from app.packages.utils import get_secret
from ..dependencies import get_current_active_user, session

router = APIRouter()


def check_book_fields(book):
    """
    Description: check if user set book correctly.
    """
    if any(
        [
            str(book.title).lower() == "string",
            str(book.author).lower() == "string",
            str(book.summary).lower() == "string",
            str(book.content).lower() == "string",
            str(book.category).lower() == "string",
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Saisie invalide, mot clef string non utilisable.",
        )
    if not isinstance(book.year_of_publication, int):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Saisie invalide, année de publication livre doit etre un entier.",
        )
    return True


@router.get("/api/v1/books/", tags=["BOOKS"])
async def view_books(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books return a list of books. Each book is a dictionnary.
    """
    books = database_crud_commands.view_all_instances(session, models.Book)
    return books


def get_user_email(user_id: int):
    """ get_user_email returns the user email """
    session = session_commands.get_a_database_session()
    user = session.query(models.User).filter(models.User.id == user_id).first()
    session.close()
    return user.email


@router.get("/api/v1/books/download/", tags=["BOOKS"])
async def download_books(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    download_books triggers a Celery task which consist to email the user with published books as a pdf file.
    """

    user_email = get_user_email(current_user.id)
    celery_app = Celery(
        broker=get_secret("/run/secrets/CELERY_BROKER_URL"),
        backend=os.getenv("CELERY_RESULT_BACKEND")
    )

    celery_app.send_task("generate_pdf_and_send_email_task", args=(user_email,), retry=True)
    logs_context = {"current_user": f"{current_user.username}"}
    log_events.log_event("[200] FastAPI - Téléchargement des livres.", logs_context)
    return {
        "detail": f"Demande reçue, vous allez recevoir par email à {user_email} les livres publiés."
    }


@router.get("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def view_book(
    book_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books return a book.
    """
    book = database_crud_commands.get_instance(session, models.Book, book_id)
    if book is not None:
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_id": book_id,
            "book_title": book.title,
        }
        log_events.log_event("[200] FastAPI - Consultation livre.", logs_context)
        return book

    logs_context = {"current_user": f"{current_user.username}", "book_id": book_id}
    log_events.log_event("[404] FastAPI - Consultation livre inconnu.", logs_context)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="FastAPI - Consultation livre inconnu.",
    )


@router.post("/api/v1/books/", tags=["BOOKS"])
async def post_book(
    book: NewBookModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    add a book.
    """
    check_book_fields(book)
    category = str(book.category).lower()
    try:
        category_id = (
            session.query(models.BookCategory)
            .filter(models.BookCategory.title == category)
            .first()
            .id
        )
    except Exception:
        logs_context = {"username": f"{str(current_user.username).lower()}"}
        log_events.log_event(
            "[404] FastAPI - Utilisateur veut ajouter un livre avec catégorie inconnue.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saisie invalide, categorie livre non connue.",
        )
    new_book = models.Book(
        title=book.title,
        author=book.author,
        summary=book.summary,
        content=book.content,
        category=category_id,
        year_of_publication=book.year_of_publication,
        book_picture_name="dummy_blank_book.png",
        user_id=current_user.id,
    )
    logs_context = {
        "current_user": f"{current_user.username}",
        "book_title": new_book.title,
    }
    log_events.log_event("[200] FastAPI - Ajout livre.", logs_context)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


@router.patch("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def partial_update_book(
    book_id: int,
    book_updated: UpdateBookModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    update partially a book instance.
    """
    book = database_crud_commands.get_instance(session, models.Book, book_id)
    if not book:
        logs_context = {"username": f"{str(current_user.username).lower()}"}
        log_events.log_event(
            "[404] FastAPI - Utilisateur veut mettre à jour partiellement un livre inconnu.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre avec id {book_id} inexistant.",
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event("[403] FastAPI - Mise à jour partielle d'un livre refusée.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent mettre à jour le livre",
        )

    if current_user.id == book.user_id or current_user.username == "admin":
        if book_updated.title is not None:
            book.title = book_updated.title
        if book_updated.author is not None:
            book.author = book_updated.author
        if book_updated.summary is not None:
            book.summary = book_updated.summary
        if book_updated.category is not None:
            category = str(book_updated.category).lower()
            try:
                category_id = (
                    session.query(models.BookCategory)
                    .filter(models.BookCategory.title == category)
                    .first()
                    .id
                )
            except Exception:
                logs_context = {"username": f"{str(current_user.username).lower()}"}
                log_events.log_event(
                    "[404] FastAPI - Utilisateur veut mettre à jour un livre avec catégorie inconnue.",
                    logs_context,
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Saisie invalide, categorie livre non prevue.",
                )
            book.category = category_id
        if book_updated.year_of_publication is not None:
            book.year_of_publication = book_updated.year_of_publication
        book.book_picture_name = "dummy_blank_book.png"
        check_book_fields(book)
        session.query(models.Book).where(models.Book.id == book_id).update(
            book.get_json_for_update()
        )
        session.commit()
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book.title,
        }
        log_events.log_event("[200] FastAPI - Mise à jour livre.", logs_context)
        return book


@router.put("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def update_book(
    book_id: int,
    book_updated: NewBookModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    full update of a book instance.
    """
    book = database_crud_commands.get_instance(session, models.Book, book_id)
    if not book:
        logs_context = {"username": f"{str(current_user.username).lower()}"}
        log_events.log_event(
            "[404] FastAPI - Utilisateur veut mettre à jour un livre inconnu.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre avec id {book_id} inexistant.",
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event("[403] FastAPI - Mise à jour livre refusée.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent mettre à jour le livre",
        )

    check_book_fields(book_updated)
    category = str(book_updated.category).lower()
    try:
        category_id = (
            session.query(models.BookCategory)
            .filter(models.BookCategory.title == category)
            .first()
            .id
        )
    except Exception:
        logs_context = {"username": f"{str(current_user.username).lower()}"}
        log_events.log_event(
            "[404] FastAPI - Utilisateur veut mettre à jour un livre avec catégorie inconnue.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saisie invalide, categorie livre non connue.",
        )
    new_book = models.Book(
        title=book_updated.title,
        author=book_updated.author,
        summary=book_updated.summary,
        content=book_updated.content,
        category=category_id,
        publication_date=book.publication_date,
        year_of_publication=book_updated.year_of_publication,
        book_picture_name="dummy_blank_book.png",
        user_id=book.user_id,
    )
    logs_context = {
        "current_user": f"{current_user.username}",
        "book_title": new_book.title,
    }
    log_events.log_event("[200] FastAPI - Ajout livre.", logs_context)
    session.query(models.Book).where(models.Book.id == book_id).update(
        new_book.get_json_for_update()
    )
    session.commit()
    return new_book


@router.delete("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def delete_book(
    book_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_book allows to delete a book base on id
    """
    book = database_crud_commands.get_instance(session, models.Book, book_id)
    if book:
        if current_user.id == book.user_id:
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": book.title,
            }
            log_events.log_event("[204] FastAPI - Suppression livre.", logs_context)
            session.delete(book)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"Livre avec id {book_id} supprimé.",
            )
        logs_context = {
            "current_user": f"{current_user.username}",
            "book_title": book.title,
        }
        log_events.log_event("[403] FastAPI - Suppression livre refusée.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent supprimer son livre.",
        )
    logs_context = {
        "current_user": f"{current_user.username}",
    }
    log_events.log_event("[404] FastAPI - Suppression livre inconnu.", logs_context)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Livre avec id {book_id} inexistant.",
    )
