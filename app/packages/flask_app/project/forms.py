""" The Flask forms definitions """

import datetime as dt
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, EmailField, IntegerField, FieldList, Form, FormField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange

from app.packages import settings
from app.packages.database.commands import session_commands
from app.packages.database.models.models import BookCategory


class LoginForm(FlaskForm):
    """
    Description: the login FlaskForm form.
    """

    login = StringField(
        label="NOM UTILISATEUR", validators=[DataRequired(), Length(min=3, max=125)]
    )
    password = PasswordField(
        "MOT DE PASSE", validators=[DataRequired(), Length(min=3, max=125)]
    )
    email = EmailField("EMAIL", validators=[DataRequired(), Email()])


class RegisterForm(FlaskForm):
    """
    Description: the register FlaskForm form.
    """

    login = StringField(
        "NOM UTILISATEUR", validators=[DataRequired(), Length(min=3, max=125)]
    )
    password = PasswordField(
        "MOT DE PASSE", validators=[DataRequired(), Length(min=3, max=125)]
    )
    password_check = PasswordField(
        "CONFIRMER MOT DE PASSE", validators=[DataRequired(), Length(min=3, max=125)]
    )
    email = EmailField("EMAIL", validators=[DataRequired(), Email()])


class CreateUserForm(FlaskForm):
    """
    Description: the create user FlaskForm form.
    """

    login = StringField(
        "NOM UTILISATEUR", validators=[DataRequired(), Length(min=3, max=125)]
    )
    password = PasswordField(
        "MOT DE PASSE", validators=[DataRequired(), Length(min=3, max=125)]
    )
    password_check = PasswordField(
        "CONFIRMER MOT DE PASSE", validators=[DataRequired(), Length(min=3, max=125)]
    )
    email = EmailField("EMAIL", validators=[DataRequired(), Email()])


class AddCategoryBookForm(FlaskForm):
    """
    Description: the add category book FlaskForm form.
    """
    title = StringField(
        label="CATEGORIE", validators=[DataRequired(), Length(min=3, max=50)]
    )


class UpdateBookCategoryForm(FlaskForm):
    """
    Description: the update category book FlaskForm form.
    """
    title = StringField(
        label="CATEGORIE", validators=[DataRequired(), Length(min=3, max=50)]
    )


class BookForm(FlaskForm):
    """
    Description: the book FlaskForm form.
    """
    max_year = dt.date.today().year
    def __init__(self, books_categories=None):
        super().__init__()
        if books_categories:
            self.categories.choices = books_categories

    def validate_category(form, field):
        if field.data not in books_categories:
            raise ValidationError("Catégorie livre non prévue")

    title = StringField(
        label="TITRE", validators=[DataRequired(), Length(min=3, max=80)]
    )
    summary = StringField(
        label="SOUS-TITRE", validators=[DataRequired(), Length(min=3, max=160)]
    )
    content = TextAreaField(
        label="DESCRIPTION", validators=[DataRequired(), Length(max=2500)]
    )
    categories = SelectField("CATEGORIES", choices="", validators=[DataRequired()])
    year_of_publication = IntegerField(
        label="ANNEE PUBLICATION",
        validators=[DataRequired(), NumberRange(min=1, max=max_year)],
    )
    author = StringField(
        label="AUTEUR", validators=[DataRequired(), Length(min=3, max=120)]
    )
    photo = FileField(
        "IMAGE",
        validators=[
            FileRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png"], "Seuls format autorisés: .jpg, .jpeg, .png!"
            ),
        ],
    )


class UpdateBookForm(FlaskForm):
    """
    Description: the update book FlaskForm form.
    """
    max_year = dt.date.today().year
    def __init__(
        self,
        books_categories=None,
        book=None
    ):
        super().__init__()
        if books_categories:
            self.categories.choices = books_categories
        if book:
            self.title.data = book.title
            self.summary.data = book.summary
            self.content.data = book.content
            self.author.data = book.author
            if book.year_of_publication is not None:
                self.year_of_publication.data = book.year_of_publication
            else:
                self.year_of_publication.data = ""

    def validate_category(form, field):
        if field.data not in books_categories:
            raise ValidationError("Catégorie livre non prévue")

    title = StringField(
        label="TITRE", validators=[DataRequired(), Length(min=3, max=80)]
    )
    summary = StringField(
        label="SOUS-TITRE", validators=[DataRequired(), Length(min=3, max=160)]
    )
    content = TextAreaField(
        label="DESCRIPTION", validators=[DataRequired(), Length(max=2500)]
    )
    categories = SelectField(
        "CATEGORIES",
        choices="",
        coerce=int,
        validators=[DataRequired()]
    )
    year_of_publication = IntegerField(
        label="ANNEE PUBLICATION",
        validators=[DataRequired(), NumberRange(min=1, max=max_year)],
    )
    author = StringField(
        label="AUTEUR", validators=[DataRequired(), Length(min=3, max=120)]
    )
    photo = FileField(
        "IMAGE",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"], "Seuls format autorisés: .jpg, .jpeg, .png!"
            ),
        ],
    )


class CommentForm(FlaskForm):
    """
    Description: the comment FlaskForm form.
    """
    comment_text = TextAreaField(
        "COMMENTAIRE", validators=[DataRequired(), Length(min=3, max=500)]
    )


class UpdateCommentForm(FlaskForm):
    """
    Description: the update comment FlaskForm form.
    """
    comment_text = TextAreaField(
        "COMMENTAIRE", validators=[DataRequired(), Length(min=3, max=500)]
    )


class ContactForm(FlaskForm):
    """
    Description: the contact FlaskForm form.
    """
    name = StringField("NOM", validators=[DataRequired()])
    email = EmailField("EMAIL", validators=[DataRequired()])
    message = TextAreaField("MESSAGE", validators=[DataRequired(), Length(min=3, max=1800)])


class DeleteBookCategoryForm(FlaskForm):
    """
    Description: the delete book category FlaskForm form.
    """
    pass


class DeleteBookForm(FlaskForm):
    """
    Description: the delete book FlaskForm form.
    """
    pass


class DeleteCommentForm(FlaskForm):
    """
    Description: the delete comment FlaskForm form.
    """
    pass


class DeleteUserForm(FlaskForm):
    """
    Description: the delete user FlaskForm form.
    """
    pass
