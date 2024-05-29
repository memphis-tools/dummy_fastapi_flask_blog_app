from pydantic import BaseModel, Field
from enum import Enum
import datetime as dt
from typing import Optional


class Token(BaseModel):
    """FastAPI token class"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """FastAPI token data class"""

    username: str | None = None


class BookCategoryModel(BaseModel):
    """FastAPI Book Category class"""

    id: int
    title: str


class NewBookCategoryModel(BaseModel):
    """FastAPI new Book Category class"""

    title: str


class UpdateBookCategoryModel(BaseModel):
    """FastAPI update Book Category class"""

    title: str


class StarredModel(BaseModel):
    """FastAPI Starred class"""

    user_id: int


class CommentModel(BaseModel):
    """FastAPI Comment class"""

    id: int
    text: str
    publication_date: dt.datetime
    author_id: int
    book_id: int


class CommentReducedModel(BaseModel):
    """FastAPI Reduced Comment class"""

    id: int
    author_id: int
    book_id: int


class NewCommentModel(BaseModel):
    """FastAPI new Comment class"""

    text: str


class UpdateCommentModel(BaseModel):
    """FastAPI update Comment class"""

    text: str


class QuoteModel(BaseModel):
    """FastAPI Quote class"""

    id: int
    author: str
    book_title: str
    quote: str


class NewQuoteModel(BaseModel):
    """FastAPI new Quote class"""

    author: str = Field(title="Name of the book's author", min_length=3)
    book_title: str = Field(title="Title of the book", min_length=3)
    quote: str = Field(title="Citation from the book", min_length=3)


class BookModel(BaseModel):
    """FastAPI Book class"""

    id: int
    title: str
    author: str
    summary: str
    content: str
    category: str
    year_of_publication: int
    publication_date: dt.datetime
    user_id: int
    book_comments: CommentReducedModel | None = None
    starred: StarredModel | None = None


class BookReducedModel(BaseModel):
    """FastAPI Reduced Book class"""

    id: int
    title: str
    author: str
    category: str
    year_of_publication: int
    publication_date: dt.datetime
    book_comments: CommentReducedModel | None = None
    starred: StarredModel | None = None


class NewBookModel(BaseModel):
    """FastAPI new Book class"""

    title: str
    author: str
    summary: str
    content: str
    category: str
    year_of_publication: int


class UpdateBookModel(BaseModel):
    """FastAPI update Book class"""

    title: Optional[str] | None = None
    author: Optional[str] | None = None
    summary: Optional[str] | None = None
    content: Optional[str] | None = None
    category: Optional[str] | None = None
    year_of_publication: Optional[int] | None = None


class Role(str, Enum):
    """FastAPI Role class"""

    admin = "admin"
    user = "user"


class UserModel(BaseModel):
    """FastAPI User class"""

    id: int
    username: str
    role: Role
    disabled: bool | None = False
    books: BookReducedModel | None = None


class UserInDB(UserModel):
    """FastAPI User password class"""

    hashed_password: str


class NewUserInDBModel(BaseModel):
    """FastAPI new User class"""

    username: str
    email: str
    password: str
    password_check: str
    role: str | None = None
    disabled: bool | None = False


class UpdateUserModel(BaseModel):
    """FastAPI update User class"""

    username: str | None = None
    email: str | None = None
    role: str | None = None
    disabled: bool | None = False


class UpdateUserPasswordInDB(BaseModel):
    """FastAPI update User password class"""

    current_password: str
    new_password: str
    new_password_check: str


class UpdateUserEmailInDB(BaseModel):
    """FastAPI update User email class"""

    email: str
