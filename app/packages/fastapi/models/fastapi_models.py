from pydantic import BaseModel
from enum import Enum
import datetime as dt
from typing import Optional


class Token(BaseModel):
    """ FastAPI token class """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """ FastAPI token data class """
    username: str | None = None


class BookCategoryModel(BaseModel):
    """ FastAPI Book Category class """
    id: int
    title: str


class NewBookCategoryModel(BaseModel):
    """ FastAPI new Book Category class """
    title: str


class UpdateBookCategoryModel(BaseModel):
    """ FastAPI update Book Category class """
    title: str


class BookModel(BaseModel):
    """ FastAPI Book class """
    id: int
    title: str
    author: str
    summary: str
    content: str
    category: str
    year_of_publication: int
    publication_date: dt.datetime
    book_picture_name: str
    user_id: int
    nb_comments: int
    nb_starred: int


class NewBookModel(BaseModel):
    """ FastAPI new Book class """
    title: str
    author: str
    summary: str
    content: str
    category: str
    year_of_publication: int
    book_picture_name: str


class UpdateBookModel(BaseModel):
    """ FastAPI update Book class """
    title: Optional[str] | None = None
    author: Optional[str] | None = None
    summary: Optional[str] | None = None
    content: Optional[str] | None = None
    category: Optional[str] | None = None
    year_of_publication: Optional[int] | None = None
    book_picture_name: Optional[str] | None = None


class Role(str, Enum):
    """ FastAPI Role class """
    admin = "admin"
    user = "user"


class UserModel(BaseModel):
    """ FastAPI User class """
    id: int
    username: str
    email: str | None = None
    role: Role
    disabled: bool | None = False
    nb_publications: int
    nb_comments: int


class UserInDB(UserModel):
    """ FastAPI User password class """
    hashed_password: str


class NewUserInDBModel(BaseModel):
    """ FastAPI new User class """
    username: str
    email: str
    password: str
    password_check: str


class UpdateUserModel(BaseModel):
    """ FastAPI update User class """
    username: str | None = None
    email: str | None = None
    role: Role | None = None
    disabled: bool | None = False


class UpdateUserInDB(BaseModel):
    """ FastAPI update User password class """
    password: str


class CommentModel(BaseModel):
    """ FastAPI Comment class """
    id: int
    text: str
    publication_date: dt.datetime
    author_id: int
    book_id: int


class NewCommentModel(BaseModel):
    """ FastAPI new Comment class """
    text: str


class UpdateCommentModel(BaseModel):
    """ FastAPI update Comment class """
    text: str
