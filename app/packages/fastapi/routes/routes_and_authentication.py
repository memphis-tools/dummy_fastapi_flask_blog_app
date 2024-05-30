import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from app.packages import handle_passwords, log_events
from app.packages.database.commands import database_crud_commands, session_commands
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    UserModel,
    UserInDB,
    UpdateUserModel,
    UpdateUserPasswordInDB,
    NewUserInDBModel,
    NewBookModel,
    UpdateBookModel,
    NewCommentModel,
    UpdateCommentModel,
    NewBookCategoryModel,
    QuoteModel,
    NewQuoteModel,
    Token,
    TokenData,
)


# tokenUrl leads to the URI "/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app: FastAPI = FastAPI(
    title="DUMMY-OPS API", swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
# session used by the FastAPI application
session = session_commands.init_and_get_a_database_session()


def get_user(username: str):
    """get user in db"""
    user = session.query(models.User).filter_by(username=username).first()
    if user:
        return UserInDB(**user.get_json())


def verify_password(plain_password, hashed_password):
    """check password hash"""
    return check_password_hash(hashed_password, plain_password)


def get_password_hash(password):
    """get hash from password"""
    return generate_password_hash(password, "pbkdf2:sha256", salt_length=8)


def authenticate_user(username: str, password: str):
    """authenticate_user > returns an User instance"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create an access token for authenticated user"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """get the current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """return current user if not disabled"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user


@app.post("/token/", tags=["DEFAULT"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """return a jwt access token to authenticated user"""
    user = authenticate_user(str(form_data.username).lower(), form_data.password)
    if not user:
        logs_context = {"username": f"{str(form_data.username).lower()}"}
        log_events.log_event(
            "[+] FastAPI - Utilisateur inconnu cherche à obtenir un token.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom utilisateur ou mot de passe invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/v1/books/", tags=["BOOKS"])
async def view_books(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books return a list of books. Each book is a dictionnary.
    """
    books = database_crud_commands.view_all_instances(session, models.Book)
    return books


@app.get("/api/v1/books/categories/", tags=["BOOKS_CATEGORIES"])
async def view_books_categories(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books_categories return a list of books categories.
    A list element consists in a dict with 3 keys: id, name, total_books.
    Remember application admin account id is 1.
    """
    categories = database_crud_commands.view_all_categories_instances(session)
    return categories


@app.get("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
async def view_category_books(
    category_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
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


@app.post("/api/v1/books/categories/", tags=["BOOKS_CATEGORIES"])
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


@app.put("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
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


@app.delete("/api/v1/books/categories/{category_id}/", tags=["BOOKS_CATEGORIES"])
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


@app.get("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def view_book(
    book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
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
    else:
        logs_context = {"current_user": f"{current_user.username}", "book_id": book_id}
        log_events.log_event("[+] FastAPI - Consultation livre inconnu.", logs_context)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FastAPI - Consultation livre inconnu.",
        )


@app.get("/api/v1/users/{user_id}/books/", tags=["USERS"])
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


@app.post("/api/v1/register/", tags=["DEFAULT"])
async def register(user: NewUserInDBModel):
    """
    register new user.
    """
    if any(
        [
            str(user.username) == "string",
            str(user.email) == "string",
            str(user.password) == "string",
            str(user.password_check) == "string",
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, mot clef string non utilisable.",
        )
    valid_password = handle_passwords.check_password(str(user.password))
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe trop simple, essayez de nouveau.",
        )
    hashed_password = generate_password_hash(
        user.password, "pbkdf2:sha256", salt_length=8
    )
    user_in_db = (
        session.query(models.User)
        .filter_by(username=str(user.username).lower())
        .first()
    )
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom utilisateur existe deja, veuillez le modifier",
        )
    user_email = (
        session.query(models.User).filter_by(email=str(user.email).lower()).first()
    )
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email existe deja en base"
        )
    if user.password != user.password_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mots de passe ne correspondent pas",
        )
    else:
        new_user = models.User(
            username=str(user.username).lower(),
            email=str(user.email).lower(),
            hashed_password=hashed_password,
        )
        logs_context = {
            "username": f"{str(user.username).lower()}",
            "email": f"{str(user.email).lower()}",
        }
        log_events.log_event("[+] FastAPI - Création compte utilisateur.", logs_context)
        session.add(new_user)
        session.commit()
        return new_user


@app.post("/api/v1/users/", tags=["USERS"])
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
    else:
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
    if type(book.year_of_publication) is not int:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, annee publication livre doit etre un entier.",
        )
    return True


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


@app.post("/api/v1/books/", tags=["BOOKS"])
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


@app.patch("/api/v1/books/{book_id}/", tags=["BOOKS"])
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
            detail=f"Livre avec id {book_id} inexistant"
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event(
            "[+] FastAPI - Book update refused.", logs_context
        )
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


@app.put("/api/v1/books/{book_id}/", tags=["BOOKS"])
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
            detail=f"Livre avec id {book_id} inexistant"
        )

    if current_user.id != book.user_id and current_user.username != "admin":
        logs_context = {
            "current_user": current_user.username,
            "book_title": book.title,
        }
        log_events.log_event(
            "[+] FastAPI - Book update refused.", logs_context
        )
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


@app.get("/api/v1/users/", tags=["USERS"])
async def view_users(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_users return a list of users and all their books and comments. Each user is a dictionnary.
    """
    users = database_crud_commands.view_all_instances(session, models.User)
    return users


@app.get("/api/v1/users/{user_id}/", tags=["USERS"])
async def view_user(
    user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_user return an user.
    """
    user = database_crud_commands.get_instance(session, models.User, user_id)
    return user


@app.patch("/api/v1/users/{user_id}/", tags=["USERS"])
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
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur",
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant",
    )


@app.put("/api/v1/users/{user_id}/", tags=["USERS"])
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
        detail=f"Utilisateur avec id {user_id} inexistant",
    )


@app.put("/api/v1/users/{user_id}/password/", tags=["USERS"])
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
            else:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Mots de passe non renseignés",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur",
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur avec id {user_id} inexistant",
    )


@app.get("/api/v1/users/{user_id}/comments/", tags=["USERS"])
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
        detail=f"Utilisateur avec id {user_id} inexistant",
    )


@app.get("/api/v1/books/comments/all/", tags=["COMMENTS"])
async def view_comments(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_comments return a list of comments. Each comment is a dictionnary
    """
    comments = database_crud_commands.view_all_instances(session, models.Comment)
    return comments


@app.get("/api/v1/books/comments/{comment_id}/", tags=["COMMENTS"])
async def view_comment(
    comment_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    """
    view_comment return a comment.
    """
    comment = database_crud_commands.get_instance(session, models.Comment, comment_id)
    return comment


@app.post("/api/v1/books/comments/", tags=["COMMENTS"])
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
        detail=f"Livre avec id {book_id} inexistant",
    )


@app.put("/api/v1/books/comments/{comment_id}/", tags=["COMMENTS"])
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
        detail=f"commentaire avec id {comment_id} inexistant",
    )


@app.get("/api/v1/books/{book_id}/comments/", tags=["COMMENTS"])
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
    comments = session.query(models.Comment).where(models.Comment.book_id == book_id).all()
    return comments


@app.delete("/api/v1/books/{book_id}/comments/{comment_id}/", tags=["COMMENTS"])
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
                detail=f"commentaire avec id {comment_id} supprimé",
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
        detail=f"commentaire avec id {comment_id} inexistant",
    )


@app.delete("/api/v1/users/{user_id}/", tags=["USERS"])
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
            detail=f"Utilisateur avec id {user_id} inexistant",
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
    else:
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


@app.delete("/api/v1/books/{book_id}/", tags=["BOOKS"])
async def delete_book(
    book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
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
        detail=f"Livre avec id {book_id} inexistant",
    )


@app.get("/api/v1/quotes/", tags=["QUOTES"])
async def get_quotes(
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    """return quotes"""
    if current_user.role == "admin":
        quotes = database_crud_commands.view_all_instances(session, models.Quote)
        return quotes
    else:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event(
            "[+] FastAPI - Consultation citations refusee, vous n'etes pas admin.",
            logs_context,
        )
        raise HTTPException(
            status_code=status. HTTP_403_FORBIDDEN,
            detail="Seul l'admin peut consulter les citations",
        )


@app.get("/api/v1/quotes/{quote_id}/", tags=["QUOTES"])
async def get_quote(
    quote_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)]
) -> QuoteModel:
    """return a quote based on id"""
    if current_user.role == "admin":
        quote = database_crud_commands.get_instance(session, models.Quote, quote_id)
        return quote
    else:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event(
            "[+] FastAPI - Consultation citation refusee, vous n'etes pas admin.",
            logs_context,
        )
        raise HTTPException(
            status_code=status. HTTP_403_FORBIDDEN,
            detail="Seul l'admin peut consulter une citation",
        )


@app.post("/api/v1/quotes/", tags=["QUOTES"])
async def add_quote(
    quote: NewQuoteModel,
    current_user: Annotated[UserModel, Depends(get_current_user)],
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
    else:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event(
            "[+] FastAPI - Ajout citation refusee, vous n'etes pas admin.",
            logs_context,
        )
        raise HTTPException(
            status_code=status. HTTP_403_FORBIDDEN,
            detail="Seul l'admin peut ajouter une citation",
        )


@app.delete("/api/v1/quotes/{quote_id}/", tags=["QUOTES"])
async def delete_quote(
    quote_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
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
    else:
        logs_context = {
            "current_user": f"{current_user.username}",
        }
        log_events.log_event(
            "[+] FastAPI - Suppression citation refusee, vous n'etes pas admin.",
            logs_context,
        )
        raise HTTPException(
            status_code=status. HTTP_403_FORBIDDEN,
            detail="Seul l'admin peut supprimer une citation",
        )
