"""The FastAPI routes for users"""


from werkzeug.security import generate_password_hash
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends, HTTPException, status

from app.packages import handle_passwords, log_events
from app.packages.database.commands import database_crud_commands
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    UserModel,
    UpdateUserModel,
    UpdateUserPasswordInDB,
    NewUserInDBModel,
)
from ..dependencies import get_current_active_user, session, authenticate_user

router = APIRouter()


@router.get("/api/v1/users/{user_id}/books/", tags=["USERS"])
async def user_books(
    user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books from a valid user return his books.
    """
    user = session.get(models.User, user_id)
    if user:
        books = database_crud_commands.view_all_user_books(session, user_id)
        return books
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Aucun Utilisateur avec id {user_id} en base",
    )


@router.post("/api/v1/users/", tags=["USERS"])
async def add_user(
    user: NewUserInDBModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    Add a new user. Only admin has this privilege.
    """
    user.username = str(user.username).lower()
    user.email = str(user.email).lower()
    existing_user = (
        session.query(models.User)
        .filter_by(username=str(user.username).lower())
        .first()
    )
    existing_email = (
        session.query(models.User).filter_by(email=str(user.email).lower()).first()
    )
    hashed_password = generate_password_hash(
        user.password, "pbkdf2:sha256", salt_length=8
    )
    valid_password = handle_passwords.check_password(user.password)
    if current_user.role == "admin":
        if not valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mot de passe trop simple, essayez de nouveau.",
            )
        if not existing_user and not existing_email:
            new_user = models.User(
                username=str(user.username).lower(),
                email=str(user.email).lower(),
                hashed_password=hashed_password,
            )
            session.add(new_user)
            session.commit()
            return {"200": f"user {str(user.username).lower()} added"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur existe deja"
        )

    logs_context = {
        "current_user": f"{current_user.username}",
        "user_to_add": user.username,
    }
    log_events.log_event(
        "[+] FastAPI - Ajout utilisateur refusee, vous n'etes pas admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Seul l'admin peut ajouter un utilisateur"
    )


@router.get("/api/v1/users/", tags=["USERS"])
async def view_users(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_users return a list of users and all their books and comments. Each user is a dictionnary.
    """
    users = database_crud_commands.view_all_instances(session, models.User)
    return users


@router.get("/api/v1/users/{user_id}/", tags=["USERS"])
async def view_user(
    user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_user return an user.
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    return user


@router.patch("/api/v1/users/{user_id}/", tags=["USERS"])
async def partial_update_user(
    user_id: int,
    user_updated: UpdateUserModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    update partially an user instance.
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    if user:
        if current_user.id == user.id or current_user.username == "admin":
            if user_updated.username is not None:
                existing_user = (
                    session.query(models.User)
                    .filter_by(username=str(user_updated.username).lower())
                    .first()
                )
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Nom utilisateur {user_updated.username} existe déjà."
                    )
            if user_updated.email is not None:
                existing_email = (
                    session.query(models.User).filter_by(email=str(user_updated.email).lower()).first()
                )
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Email utilisateur {user.email} existe déjà."
                    )
            logs_context = {
                "current_user": f"{current_user.username}",
                "user_to_update": user_updated.username,
            }
            if user_updated.role is not None:
                if not database_crud_commands.is_user_role_valid(str(user_updated.role).lower()):
                    raise HTTPException(
                        status_code=status. HTTP_404_NOT_FOUND, detail="Role inconnu."
                    )
                if str(user_updated.role).lower() == "admin" and not current_user.role == "admin":
                    log_events.log_event(
                        "[+] FastAPI - Mise a jour role utilisateur en admin refusee, vous n'etes pas admin.",
                        logs_context,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Affecter role admin autorisé aux seuls admins."
                    )
            if str(user_updated.disabled) == "True" and not current_user.role == "admin":
                log_events.log_event(
                    "[+] FastAPI - Mise a jour utilisateur refusee, vous n'etes pas admin.",
                    logs_context,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Désactiver utilisateur autorisé aux seuls admins."
                )
            if user_updated.username is not None:
                user.username = user_updated.username
            if user_updated.email is not None:
                user.email = user_updated.email
            if user_updated.role is not None:
                user.role = user_updated.role
            if user_updated.disabled is not None:
                user.disabled = user_updated.disabled
            session.query(models.User).where(models.User.id == user_id).update(
                user.get_json_for_update()
            )
            session.commit()
            session.refresh(user)
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant.",
    )


@router.put("/api/v1/users/{user_id}/", tags=["USERS"])
async def update_user(
    user_id: int,
    user_updated: NewUserInDBModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    full update of an user instance.
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    if user:
        if current_user.id == user.id or current_user.username == "admin":
            existing_user = (
                session.query(models.User)
                .filter_by(username=str(user_updated.username).lower())
                .first()
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Nom utilisateur {user_updated.username} existe déjà."
                )
            existing_email = (
                session.query(models.User).filter_by(email=str(user_updated.email).lower()).first()
            )
            hashed_password = generate_password_hash(
                user_updated.password, "pbkdf2:sha256", salt_length=8
            )
            valid_password = handle_passwords.check_password(user_updated.password)
            logs_context = {
                "current_user": f"{current_user.username}",
                "user_to_update": user.username,
            }
            if not valid_password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Mot de passe trop simple, essayez de nouveau.",
                )
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Email existe déjà."
                )
            if user_updated.role is not None:
                if not database_crud_commands.is_user_role_valid(str(user_updated.role).lower()):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Role inconnu."
                    )
                if str(user_updated.role).lower() == "admin" and not current_user.role == "admin":
                    log_events.log_event(
                        "[+] FastAPI - Mise a jour utilisateur refusee, vous n'etes pas admin.",
                        logs_context,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Affecter role admin autorisé aux seuls admins."
                    )
                user.role = str(user_updated.role).lower()
            if user_updated.disabled is not None:
                if str(user_updated.disabled) == "True" and not current_user.role == "admin":
                    log_events.log_event(
                        "[+] FastAPI - Mise a jour utilisateur refusee, vous n'etes pas admin.",
                        logs_context,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Désactiver utilisateur autorisé aux seuls admins."
                    )
            else:
                user_updated.disabled = False

            new_user = models.User(
                username=str(user_updated.username).lower(),
                email=str(user_updated.email).lower(),
                hashed_password=hashed_password,
                role=str(user_updated.role).lower(),
                disabled=user_updated.disabled
            )
            session.query(models.User).where(models.User.id == user_id).update(
                new_user.get_json_for_update()
            )
            session.commit()
            session.refresh(user)
            return user.get_json()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant.",
    )


@router.put("/api/v1/users/{user_id}/password/", tags=["USERS"])
async def update_user_password(
    user_id: int,
    user_updated: UpdateUserPasswordInDB,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    full update password of an user instance.
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    if user:
        if current_user.id == user.id or current_user.username == "admin":
            if not handle_passwords.check_password_input(
                user_updated.current_password,
                user_updated.new_password,
                user_updated.new_password_check,
            ):
                if not authenticate_user(
                    current_user.username, user_updated.current_password
                ):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Mot de passe actuel incorrect.",
                    )
                if user_updated.new_password != user_updated.new_password_check:
                    raise HTTPException(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail="Mots de passe ne correspondent pas.",
                    )
                valid_password = handle_passwords.check_password(
                    str(user_updated.new_password)
                )
                if not valid_password:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Mot de passe trop simple, essayez de nouveau.",
                    )
                user.hashed_password = generate_password_hash(
                    user_updated.new_password, "pbkdf2:sha256", salt_length=8
                )
                session.query(models.User).where(models.User.id == user_id).update(
                    user.get_json_for_update()
                )
                session.commit()
                return user

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Mots de passe non renseignés",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur",
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant.",
    )


@router.get("/api/v1/users/{user_id}/comments/", tags=["USERS"])
async def view_user_comments(
    user_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_comments return a list of comments from an user. Each comment is a dictionnary
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    if user:
        comments = database_crud_commands.view_all_user_comments(session, user.id)
        return comments
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant.",
    )


@router.delete("/api/v1/users/{user_id}/", tags=["USERS"])
async def delete_user(
    user_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_user allows to delete an user base on id
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec id {user_id} inexistant.",
        )
    if current_user.role == "admin":
        logs_context = {
            "current_user": f"{current_user.username}",
            "user_to_delete": user.username,
        }
        log_events.log_event("[+] FastAPI - Suppression utilisateur.", logs_context)
        session.delete(user)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"Utilisateur avec id {user_id} supprimé",
        )

    logs_context = {
        "current_user": f"{current_user.username}",
        "user_to_delete": user.username,
    }
    log_events.log_event(
        "[+] FastAPI - Suppression utilisateur refusée, utilisateur non admin.",
        logs_context,
    )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Seul l'admin peut supprimer un utilisateur",
    )
