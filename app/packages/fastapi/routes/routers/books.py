"""The FastAPI routes for books"""

from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.packages import log_events
from app.packages.database.commands import database_crud_commands
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    UserModel,
    NewBookModel,
    UpdateBookModel,
)
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, mot clef string non utilisable.",
        )
    if not isinstance(book.year_of_publication, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, annee publication livre doit etre un entier.",
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
        log_events.log_event("[+] FastAPI - Consultation livre.", logs_context)
        return book

    logs_context = {"current_user": f"{current_user.username}", "book_id": book_id}
    log_events.log_event("[+] FastAPI - Consultation livre inconnu.", logs_context)
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
    log_events.log_event("[+] FastAPI - Ajout livre.", logs_context)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre avec id {book_id} inexistant.",
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event("[+] FastAPI - Book update refused.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
        log_events.log_event("[+] FastAPI - Mise à jour livre.", logs_context)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Livre avec id {book_id} inexistant.",
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event("[+] FastAPI - Book update refused.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
    log_events.log_event("[+] FastAPI - Ajout livre.", logs_context)
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
            log_events.log_event("[+] FastAPI - Suppression livre.", logs_context)
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
        log_events.log_event("[+] FastAPI - Suppression livre refusée.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent supprimer son livre.",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Livre avec id {book_id} inexistant.",
    )
