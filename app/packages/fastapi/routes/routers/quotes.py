"""The FastAPI routes for quotes"""

from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

try:
    import log_events
    from database.commands import database_crud_commands
    from database.models import models
    from app.fastapi.models.fastapi_models import (
        UserModel,
        QuoteModel,
        NewQuoteModel,
    )
except ModuleNotFoundError:
    from app.packages import log_events
    from app.packages.database.commands import database_crud_commands
    from app.packages.database.models import models
    from app.packages.fastapi.models.fastapi_models import (
        UserModel,
        QuoteModel,
        NewQuoteModel,
    )
from ..dependencies import get_current_active_user, session

router = APIRouter()


@router.get("/api/v1/quotes/", tags=["QUOTES"])
async def get_quotes(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """return quotes"""
    if current_user.role == "admin":
        quotes = database_crud_commands.view_all_instances(session, models.Quote)
        return quotes

    logs_context = {
        "current_user": f"{current_user.username}",
    }
    log_events.log_event(
        "[+] FastAPI - Consultation citations refusee, vous n'etes pas admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seul l'admin peut consulter les citations",
    )


@router.get("/api/v1/quotes/{quote_id}/", tags=["QUOTES"])
async def get_quote(
    quote_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
) -> QuoteModel:
    """return a quote based on id"""
    if current_user.role == "admin":
        quote = database_crud_commands.get_instance(session, models.Quote, quote_id)
        return quote

    logs_context = {
        "current_user": f"{current_user.username}",
    }
    log_events.log_event(
        "[+] FastAPI - Consultation citation refusee, vous n'etes pas admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seul l'admin peut consulter une citation",
    )


@router.post("/api/v1/quotes/", tags=["QUOTES"])
async def add_quote(
    quote: NewQuoteModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
) -> NewQuoteModel:
    """add a quote and return it"""
    if current_user.role == "admin":
        new_quote = models.Quote(
            author=quote.author,
            book_title=quote.book_title,
            quote=quote.quote,
        )
        logs_context = {
            "current_user": f"{current_user.username}",
            "author": new_quote.author,
            "book_title": new_quote.book_title,
            "quote": new_quote.quote,
        }
        log_events.log_event("[+] FastAPI - Ajout citation.", logs_context)
        session.add(new_quote)
        session.commit()
        return new_quote

    logs_context = {
        "current_user": f"{current_user.username}",
    }
    log_events.log_event(
        "[+] FastAPI - Ajout citation refusee, vous n'etes pas admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seul l'admin peut ajouter une citation",
    )


@router.delete("/api/v1/quotes/{quote_id}/", tags=["QUOTES"])
async def delete_quote(
    quote_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_quote allows to delete a quote base on id
    """
    if current_user.role == "admin":
        quote = database_crud_commands.get_instance(session, models.Quote, quote_id)
        if quote:
            logs_context = {
                "current_user": f"{current_user.username}",
                "author": quote.author,
                "book_title": quote.book_title,
            }
            log_events.log_event("[+] FastAPI - Suppression citation.", logs_context)
            session.delete(quote)
            session.commit()
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"Citation id {quote_id} supprimée.",
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citation id {quote_id} inexistante",
        )

    logs_context = {
        "current_user": f"{current_user.username}",
    }
    log_events.log_event(
        "[+] FastAPI - Suppression citation refusee, vous n'etes pas admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Seul l'admin peut supprimer une citation",
    )
