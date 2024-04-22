import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

try:
    from app.packages import logtail_handler, settings
    from app.packages.database.commands import database_crud_commands, session_commands
    from app.packages.database.models import models
    from app.packages.fastapi.models.fastapi_models import (
        UserModel,
        UserInDB,
        UpdateUserModel,
        UpdateUserInDB,
        NewUserInDBModel,
        NewBookModel,
        UpdateBookModel,
        NewCommentModel,
        UpdateCommentModel,
        BookCategoryModel,
        NewBookCategoryModel,
        UpdateBookCategoryModel,
        Token,
        TokenData,
    )
except ModuleNotFoundError:
    from packages import logtail_handler, settings
    from packages.database.commands import database_crud_commands, session_commands
    from packages.database.models import models
    from packages.fastapi.models.fastapi_models import (
        UserModel,
        UserInDB,
        UpdateUserModel,
        UpdateUserInDB,
        NewUserInDBModel,
        NewBookModel,
        UpdateBookModel,
        NewCommentModel,
        UpdateCommentModel,
        BookCategoryModel,
        NewBookCategoryModel,
        UpdateBookCategoryModel,
        Token,
        TokenData,
    )


# tokenUrl leads to the URI "/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
app: FastAPI = FastAPI()
LOGGER = logtail_handler.logger
# session used by the FastAPI application
session = session_commands.init_and_get_a_database_session("postgresql")


def get_user(username: str):
    """ get user in db """
    user = session.query(models.User).filter_by(username=username).first()
    if user:
        return UserInDB(**user.get_json())


def verify_password(plain_password, hashed_password):
    """ check password hash """
    return check_password_hash(hashed_password, plain_password)


def get_password_hash(password):
    """ get hash from password """
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
    """ create an access token for authenticated user """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """ get the current user """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
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
    """ return current user if not disabled """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """ return a jwt access token to authenticated user """
    user = authenticate_user(str(form_data.username).lower(), form_data.password)
    if not user:
        if os.getenv("SCOPE") == "production":
            logs_context = {"user": f"{str(form_data.username).lower()}"}
            LOGGER.info(
                "[+] FastAPI - Utilisateur inconnu cherche à obtenir un token", extra=logs_context
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/api/v1/books")
async def view_books(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books return a list of books. Each book is a dictionnary.
    """
    books = database_crud_commands.view_all_instances(session, models.Book)
    return books


@app.get("/api/v1/books/categories/")
async def view_books_categories(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books_categories return a list of books categories.
    A list element consists in a dict with 3 keys: id, name, total_books.
    Remember application admin account id is 1.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status. HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    categories = database_crud_commands.view_all_categories_instances(session)
    return categories


@app.get("/api/v1/books/categories/{id}/")
async def view_category_books(
    id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_category_books return a list of books from a category.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status. HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    category = database_crud_commands.get_instance(session, models.BookCategory, id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect category id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    categories = database_crud_commands.view_all_category_books(session, id)
    return categories


@app.post("/api/v1/books/categories/")
async def add_category_books(
    book_category: NewBookCategoryModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    add_category_books a category if it has been created.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status. HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    new_book_category = models.BookCategory(
        title=book_category.title
    )
    check_book_category_fields(new_book_category)
    session.add(new_book_category)
    session.commit()
    return new_book_category


@app.put("/api/v1/books/categories/{id}/update/")
async def update_book_category(
    id: int,
    book_category_updated: UpdateBookCategoryModel,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    update_book_category return a an updated book category.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status. HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    category = database_crud_commands.get_instance(session, models.BookCategory, id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect category id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if book_category_updated.title is not None:
        check_book_category_fields(book_category_updated)
        category.title = book_category_updated.title
        session.query(models.BookCategory).where(models.BookCategory.id == id).update(
                category.get_json_for_update()
        )
        session.commit()
    return category


@app.delete("/api/v1/books/categories/{id}/delete/")
async def delete_book_category(
    id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_book_category returns 204 if category deleted.
    """
    if current_user.id != 1:
        raise HTTPException(
            status_code=status. HTTP_401_UNAUTHORIZED,
            detail="Acces reserve au seul compte admin",
            headers={"WWW-Authenticate": "Bearer"},
        )
    category = database_crud_commands.get_instance(session, models.BookCategory, id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect category id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    session.delete(category)
    session.commit()
    raise HTTPException(
        status_code= status.HTTP_204_NO_CONTENT,
        detail= f"category with id {id} removed."
    )


@app.get("/api/v1/books/{id}/")
async def view_book(
    id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_books return a book.
    """
    book = database_crud_commands.get_instance(session, models.Book, id)
    if book is not None:
        if os.getenv("SCOPE") == "production":
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_id": id,
                "book_title": book.title
            }
            LOGGER.info("[+] FastAPI - Consultation livre", extra=logs_context)
        return book
    else:
        if os.getenv("SCOPE") == "production":
            logs_context = {"current_user": f"{current_user.username}", "book_id": id}
            LOGGER.info("[+] FastAPI - Consultation livre inconnu", extra=logs_context)
        return books


@app.get("/api/v1/{user_id}/books/")
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
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun utilisateur avec id {user_id} en base"
        )


@app.post("/api/v1/register/")
async def register(
    user: NewUserInDBModel
):
    """
    register new user.
    """
    if any([
        str(user.username) == "string",
        str(user.email) == "string",
        str(user.password) == "string",
        str(user.password_check) == "string"
    ]):
        raise HTTPException(
            status_code=401,
            detail="Saisie invalide, mot clef string non utilisable."
        )
    hashed_password = generate_password_hash(
        user.password, "pbkdf2:sha256", salt_length=8
    )
    user_in_db = session.query(models.User).filter_by(username=str(user.username).lower()).first()
    if user_in_db:
        raise HTTPException(
            status_code=401,
            detail="Nom utilisateur existe deja, veuillez le modifier"
        )
    user_email = session.query(models.User).filter_by(email=str(user.email).lower()).first()
    if user_email:
        raise HTTPException(
            status_code=401,
            detail="Email existe deja en base"
        )
    if user.password != user.password_check:
        raise HTTPException(
            status_code=401,
            detail="Mots de passe ne correspondent pas"
        )
    else:
        new_user = models.User(
            username=str(user.username).lower(),
            email=str(user.email).lower(),
            hashed_password=hashed_password,
        )
        if os.getenv("SCOPE") == "production":
            logs_context = {
                "username": f"{str(user.username).lower()}",
                "email": f"{str(user.email).lower()}"
            }
            LOGGER.info("[+] Flask - Création compte utilisateur.", extra=logs_context)
        session.add(new_user)
        session.commit()
        return user


def check_book_fields(book):
    """
    Description: check if user set book correctly.
    """
    if any([
        str(book.title).lower() == "string",
        str(book.author).lower() == "string",
        str(book.summary).lower() == "string",
        str(book.content).lower() == "string",
        str(book.category).lower() == "string",
        str(book.book_picture_name).lower() == "string",
    ]):
        raise HTTPException(
            status_code=401,
            detail="Saisie invalide, mot clef string non utilisable."
        )
    if type(book.year_of_publication) is not int:
        raise HTTPException(
            status_code=401,
            detail="Saisie invalide, annee publication livre doit etre un entier."
        )
    return True


def check_book_category_fields(category):
    """
    Description: check if user set book category correctly.
    """
    if str(category.title).lower() == "string":
        raise HTTPException(
            status_code=401,
            detail="Saisie invalide, mot clef string non utilisable."
        )
    category = session.query(models.BookCategory).filter(
        models.BookCategory.title==str(category.title).lower()
    ).first()
    if category:
        raise HTTPException(
            status_code=401,
            detail="Saisie invalide, categorie existe deja."
        )


@app.post("/api/v1/books/")
async def post_book(
    book: NewBookModel, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    add a book.
    """
    check_book_fields(book)
    category = book.category
    try:
        category_id = session.query(models.BookCategory).filter(models.BookCategory.title==category).first().id
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Saisie invalide, categorie livre non connue."
        )
    new_book = models.Book(
        title=book.title,
        author=book.author,
        summary=book.summary,
        content=book.content,
        category=category_id,
        year_of_publication=book.year_of_publication,
        book_picture_name=book.book_picture_name,
        user_id=current_user.id
    )
    total_user_publications = current_user.nb_publications + 1
    current_user.nb_publications = total_user_publications
    if os.getenv("SCOPE") == "production":
        logs_context = {"current_user": f"{current_user.username}", "book_title": new_book.title}
        LOGGER.info("[+] FastAPI - Ajout livre", extra=logs_context)
    session.add(new_book)
    session.commit()
    return new_book


@app.put("/api/v1/books/{id}/")
async def update_book(
    id: int, book_updated: UpdateBookModel, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    update a book instance.
    """
    book = database_crud_commands.get_instance(session, models.Book, id)
    if book:
        if current_user.id == book.user_id or current_user.username == "admin":
            if book_updated.title is not None:
                book.title = book_updated.title
            if book_updated.author is not None:
                book.author = book_updated.author
            if book_updated.summary is not None:
                book.summary = book_updated.summary
            if book_updated.category is not None:
                category = book_updated.category
                try:
                    category_id = session.query(models.BookCategory).filter(models.BookCategory.title==category).first().id
                except Exception:
                    raise HTTPException(
                        status_code=401,
                        detail="Saisie invalide, categorie livre non prevue."
                    )
                book.category = category_id
            if book_updated.year_of_publication is not None:
                book.year_of_publication = book_updated.year_of_publication
            if book_updated.book_picture_name is not None:
                book.book_picture_name = book_updated.book_picture_name
            check_book_fields(book)
            session.query(models.Book).where(models.Book.id == id).update(
                book.get_json_for_update()
            )
            session.commit()
            if os.getenv("SCOPE") == "production":
                logs_context = {
                    "current_user": f"{current_user.username}",
                    "book_title": book.title
                }
                LOGGER.info("[+] FastAPI - Mise à jour livre", extra=logs_context)
            return book
        else:
            if os.getenv("SCOPE") == "production":
                logs_context = {
                    "current_user": f"{current_user.username}",
                    "book_title": book.title
                }
                LOGGER.info("[+] FastAPI - Mise à jour livre refusée", extra=logs_context)
            raise HTTPException(
                status_code=401,
                detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent mettre à jour le livre"
            )
    raise HTTPException(status_code=404, detail=f"book with id {id} does not exist")


@app.get("/api/v1/users")
async def view_users(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_users return a list of users and all their books and comments. Each user is a dictionnary.
    """
    books = database_crud_commands.view_all_instances(session, models.User)
    return books


@app.get("/api/v1/users/{id}/")
async def view_user(
    id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_user return an user.
    """
    user = database_crud_commands.get_instance(session, models.User, id)
    return user


@app.put("/api/v1/users/{id}/")
async def update_user(
    id: int, user_updated: UpdateUserModel, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    update an user instance.
    """
    user = database_crud_commands.get_instance(session, models.User, id)
    if user:
        if current_user.id == user.id or current_user.username == "admin":
            if user_updated.username is not None:
                user.username = user_updated.username
            if user_updated.email is not None:
                user.email = user_updated.email
            if user_updated.role is not None:
                user.role = user_updated.role
            if user_updated.disabled is not None:
                user.disabled = user_updated.disabled
            session.query(models.User).where(models.User.id == id).update(
                user.get_json_for_update()
            )
            session.commit()
            return user
        else:
            raise HTTPException(
                status_code=401,
                detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur"
            )
    raise HTTPException(status_code=404, detail=f"user with id {id} does not exist")


@app.put("/api/v1/users/{id}/password/")
async def update_user_password(
    id: int, user_updated: UpdateUserInDB, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    update password of an user instance.
    """
    user = database_crud_commands.get_instance(session, models.User, id)
    if user:
        if current_user.id == user.id or current_user.username == "admin":
            if user_updated.password is not None:
                user.hashed_password = generate_password_hash(
                    user_updated.password, "pbkdf2:sha256", salt_length=8
                )
            session.query(models.User).where(models.User.id == id).update(
                user.get_json_for_update()
            )
            session.commit()
            return user_updated
        else:
            raise HTTPException(
                status_code=401,
                detail="Seul l'utilisateur ou l'admin peuvent mettre à jour l'utilisateur"
            )
    raise HTTPException(status_code=404, detail=f"user with id {id} does not exist")


@app.get("/api/v1/comments")
async def view_comments(
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_comments return a list of comments. Each comment is a dictionnary
    """
    books = database_crud_commands.view_all_instances(session, models.Comment)
    return books


@app.get("/api/v1/comments/{id}/")
async def view_comment(
    id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    view_comment return a comment.
    """
    comment = database_crud_commands.get_instance(session, models.Comment, id)
    return comment


@app.post("/api/v1/comments/")
async def add_comment(
    comment: NewCommentModel, book_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    add a comment.
    """
    updated_book = database_crud_commands.get_instance(session, models.Book, book_id)
    new_comment = models.Comment(
        text=comment.text,
        book_id=book_id,
        author_id=current_user.id
    )
    if updated_book:
        session.add(new_comment)
        session.commit()
        total_book_comments = updated_book.nb_comments + 1
        updated_book.nb_comments = total_book_comments
        if os.getenv("SCOPE") == "production":
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": updated_book.title
            }
            LOGGER.info("[+] FastAPI - Ajout commentaire", extra=logs_context)
        return new_comment

    raise HTTPException(status_code=404, detail=f"book with id {book_id} does not exist")


@app.put("/api/v1/comments/{id}/")
async def update_comment(
    id: int, comment_updated: UpdateCommentModel, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    update a comment instance.
    """
    comment = database_crud_commands.get_instance(session, models.Comment, id)
    if comment:
        if current_user.id == comment.author_id or current_user.username == "admin":
            if comment_updated.text is not None:
                comment.text = comment_updated.text
            session.query(models.Comment).where(models.Comment.id == id).update(
                comment.get_json_for_update()
            )
            session.commit()
            return comment
        raise HTTPException(
            status_code=401,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent mettre à jour un commentaire"
        )
    raise HTTPException(status_code=404, detail=f"comment with id {id} does not exist")


@app.delete("/api/v1/books/{book_id}/comments/{id}/")
async def delete_comment(
    id: int, book_id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_comment allows to delete a comment base on id
    """
    updated_book = database_crud_commands.get_instance(session, models.Book, book_id)
    if updated_book is None:
        raise HTTPException(
            status_code=404,
            detail="Livre n'existe pas."
        )
    comment = database_crud_commands.get_instance(session, models.Comment, id)
    if comment.book_id != book_id:
        raise HTTPException(
            status_code=401,
            detail="Commentaire non rattaché au livre."
        )
    if comment:
        if current_user.id == comment.author_id:
            session.delete(comment)
            session.commit()
            total_book_comments = updated_book.nb_comments + 1
            updated_book.nb_comments = total_book_comments
            return {"204": f"comment with id {id} removed"}
        if os.getenv("SCOPE") == "production":
            logs_context = {
                "current_user": f"{current_user.username}",
                "book_title": updated_book.title,
                "comment": comment.text
            }
            LOGGER.info("[+] Flask - Suppression commentaire refusée", extra=logs_context)
        raise HTTPException(
            status_code=401,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent supprimer son commentaire"
        )
    raise HTTPException(status_code=404, detail=f"comment with id {id} does not exist")


@app.delete("/api/v1/users/{id}/")
async def delete_user(
    id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_comment allows to delete an user base on id
    """
    user = database_crud_commands.get_instance(session, models.User, id)
    if current_user.role == "admin":
        if user:
            session.delete(user)
            session.commit()
            return {"204": f"user with id {id} removed"}
        raise HTTPException(
            status_code=404,
            detail="Utilisateur n'existe pas"
        )
    else:
        if os.getenv("SCOPE") == "production":
            logs_context = {
                "current_user": f"{current_user.username}",
                "user_to_delete": user.username
            }
            LOGGER.info(
                "[+] FastAPI - Suppression utilisateur refusée, utilisateur non admin",
                extra=logs_context
            )
        raise HTTPException(
            status_code=401,
            detail="Seul l'admin peut supprimer un utilisateur"
        )
    raise HTTPException(status_code=404, detail=f"user with id {id} does not exist")


@app.delete("/api/v1/books/{id}/")
async def delete_book(
    id: int,
    current_user: Annotated[UserModel, Depends(get_current_active_user)]
):
    """
    delete_comment allows to delete a book base on id
    """
    book = database_crud_commands.get_instance(session, models.Book, id)
    if book:
        if current_user.id == book.user_id:
            if os.getenv("SCOPE") == "production":
                logs_context = {
                    "current_user": f"{current_user.username}",
                    "book_title": book.title
                }
                LOGGER.info("[+] FastAPI - Suppression livre", extra=logs_context)
            session.delete(book)
            session.commit()
            total_user_publications = current_user.nb_publications - 1
            current_user.nb_publications = total_user_publications
            raise HTTPException(
                status_code=204,
                detail= f"book with id {id} removed."
            )
        if os.getenv("SCOPE") == "production":
            logs_context = {"current_user": f"{current_user.username}", "book_title": book.title}
            LOGGER.info("[+] FastAPI - Suppression livre refusée", extra=logs_context)
        raise HTTPException(
            status_code=401,
            detail="Seul l'utilisateur l'ayant publié ou l'admin peuvent supprimer son livre."
        )
    raise HTTPException(status_code=404, detail=f"book with id {id} does not exist")
