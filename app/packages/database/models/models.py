""" all the sqlalchemy models """


import datetime
from enum import Enum
from flask_login import UserMixin

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import EmailType


BASE = declarative_base()


class Starred(BASE):
    """
    Description: a starred model related to books of the dummy blog.
    """

    __tablename__ = "starred_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users_table.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books_table.id"), primary_key=True)
    users = relationship("User", back_populates="starred")
    books = relationship("Book", back_populates="starred")

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.id

    def get_json(self):
        """
        Description: get a starred instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
        }


class Quote(BASE):
    """
    Description: a quote model for the dummy blog.
    Notice the quote does not necessary comes from a dummy blog's book.
    """

    __tablename__ = "quote_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(150), nullable=False)
    book_title = Column(String(200), nullable=False)
    quote = Column(String(500), nullable=False)

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.id

    def get_json(self):
        """
        Description: get a quote instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "author": self.author,
            "book_title": self.book_title,
            "quote": self.quote,
        }


class Comment(BASE):
    """
    Description: a comment model related to books of the dummy blog.
    """

    __tablename__ = "comments_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(500), nullable=False)
    publication_date = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow()
    )
    author_id = Column(Integer, ForeignKey("users_table.id"))
    book_id = Column(Integer, ForeignKey("books_table.id"))
    comment_author = relationship("User", back_populates="comments")
    comment_book = relationship("Book", back_populates="book_comments")

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.text

    def get_json(self):
        """
        Description: get a comment instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "text": self.text,
            "publication_date": self.publication_date.strftime("%d-%m-%Y %H:%M:%S"),
            "author_id": self.author_id,
            "book_id": self.book_id,
        }

    def get_json_for_update(self):
        """
        Description:
        Get a comment instance as a json dict without id (when we list them from FastAPI)
        """
        return {
            "text": self.text,
        }


class BookCategory(BASE):
    """
    Description: a book category model for the dummy blog.
    """

    __tablename__ = "book_categories_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.title

    def get_json(self):
        """
        Description: get a category book instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "title": self.title,
        }

    def get_json_for_update(self):
        """
        Description:
        Get a category book instance as a json dict without id (when we list them from FastAPI)
        """
        return {
            "title": self.title,
        }


class Book(BASE):
    """
    Description: a book model for the dummy blog.
    """

    __tablename__ = "books_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(String(2500), nullable=False)
    author = Column(String(150), nullable=False)
    category = Column(Integer, ForeignKey("book_categories_table.id"), nullable=True)
    year_of_publication = Column(Integer, nullable=True)
    book_picture_name = Column(String(250), nullable=False)
    publication_date = Column(
        DateTime(timezone=True), default=datetime.datetime.utcnow()
    )
    user_id = Column(Integer, ForeignKey("users_table.id"))
    user_books = relationship("User", back_populates="books")
    book_comments = relationship(
        "Comment", back_populates="comment_book", cascade="all, delete-orphan"
    )
    starred = relationship("Starred", back_populates="books", cascade="delete, delete-orphan")

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.title

    def get_json(self):
        """
        Description: get a book instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "summary": self.summary,
            "content": self.content,
            "category": self.category,
            "year_of_publication": self.year_of_publication,
            "publication_date": self.publication_date,
            "user_id": self.user_id,
            "book_comments": self.book_comments,
            "starred": self.starred,
        }

    def get_json_for_update(self):
        """
        Description:
        Get a book instance as a json dict without id (when we list them from FastAPI)
        """
        return {
            "title": self.title,
            "author": self.author,
            "summary": self.summary,
            "content": self.content,
            "category": self.category,
            "year_of_publication": self.year_of_publication,
            "publication_date": self.publication_date,
            "book_picture_name": self.book_picture_name,
            "user_id": self.user_id,
        }


class Role(str, Enum):
    """
    Description: a role model for users of the dummy blog.
    """
    R1 = "admin"
    R2 = "user"


class User(BASE, UserMixin):
    """
    Description: an user model for the dummy blog.
    """

    __tablename__ = "users_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(200), nullable=False, unique=True)
    hashed_password = Column(String(200), nullable=False)
    email = Column(EmailType, nullable=False)
    role = Column(String(20), default=Role.R2)
    is_active = Column(Boolean, default=True)
    books = relationship(
        "Book", back_populates="user_books", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="comment_author", cascade="delete, delete-orphan"
    )
    starred = relationship("Starred", back_populates="users", cascade="delete, delete-orphan")
    disabled = Column(Boolean, default=True)

    def __str__(self, *args, **kwargs):
        """
        Description: rewrite the __str__ function for the model object.
        """
        return self.username.capitalize()

    def get_json(self):
        """
        Description: get an user instance as a json dict during general application execution.
        """
        return {
            "id": self.id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "email": self.email,
            "role": self.role,
        }

    def get_restricted_json(self):
        """
        Description:
        Get an user instance as a json dict without hashed passwords (when we list them from FastAPI)
        """
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "books": self.books,
            "comments": self.comments,
            "starred": self.starred,
        }

    def get_json_for_update(self):
        """
        Description:
        Get a user instance as a json dict without id (when we list them from FastAPI)
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "email": self.email,
            "role": self.role,
        }

    def get_id(self):
        return self.id
