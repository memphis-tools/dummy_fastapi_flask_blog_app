"""The FastAPI routes for books categories"""


from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.packages import log_events
from app.packages.database.commands import database_crud_commands
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    UserModel,
    NewBookCategoryModel,
)
from ..dependencies import get_current_active_user, session

router = APIRouter()


def check_book_category_fields(category):
    """
    Description: check if user set book category correctly.
    """
    if str(category.title).lower() == "string":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, mot clef string non utilisable.",
        )
    category = (
        session.query(models.BookCategory)
        .filter(models.BookCategory.title == str(category.title).lower())
        .first()
    )
    if category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, categorie existe deja.",
        )


@router.get("/api/v1/books/categories/", tags=["BOOKS_CATEGORIES"])
async def view_books_categories(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_books_categories return a list of books categories.
    A list element consists in a dict with 3 keys: id, name, total_books.
    Remember application admin account id is 1.
    """
    categories = database_crud_commands.view_all_categories_instances(session)
    return categories


@router.get("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
async def view_category_books(
    category_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_category_books return a list of books from a category.
    """
    category_books = database_crud_commands.view_all_category_books(
        session, category_id
    )
    if len(category_books) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catégorie avec id {category_id} inexistante.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return category_books


@router.post("/api/v1/books/categories/", tags=["BOOKS_CATEGORIES"])
async def add_category_books(
    book_category: NewBookCategoryModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    add_category_books adds category and return it if it has been created.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin"
        )
    new_book_category = models.BookCategory(title=str(book_category.title).lower())
    check_book_category_fields(new_book_category)
    logs_context = {
        "current_user": f"{current_user.username}",
        "new_book_category": new_book_category.title,
    }
    log_events.log_event("[+] FastAPI - Ajout catégorie livre.", logs_context)
    session.add(new_book_category)
    session.commit()
    session.refresh(new_book_category)
    return new_book_category


@router.put("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
async def update_book_category(
    category_id: int,
    book_category_updated: NewBookCategoryModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    update_book_category return a an updated book category.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
        )
    category = database_crud_commands.get_instance(
        session, models.BookCategory, category_id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catégorie avec id {category_id} inexistante.",
        )
    if book_category_updated.title is not None:
        check_book_category_fields(book_category_updated)
        logs_context = {
            "current_user": f"{current_user.username}",
            "updated_category_old": category.title,
            "updated_category_new": str(book_category_updated.title).lower(),
        }
        log_events.log_event("[+] FastAPI - Mise à jour catégorie livre.", logs_context)
        category.title = str(book_category_updated.title).lower()
        session.query(models.BookCategory).where(
            models.BookCategory.id == category_id
        ).update(category.get_json_for_update())
        session.commit()
        session.refresh(category)
    return category


@router.delete("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
async def delete_book_category(
    category_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    delete_book_category returns 204 if category deleted.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
        )
    category = database_crud_commands.get_instance(
        session, models.BookCategory, category_id
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="catégorie avec id {category_id} inexistante",
        )
    logs_context = {
        "current_user": f"{current_user.username}",
        "category_to_delete": category.title,
    }
    log_events.log_event("[+] FastAPI - Suppression catégorie livre.", logs_context)
    session.delete(category)
    session.commit()
    raise HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail=f"catégorie avec id {category_id} supprimée.",
    )
