""" The Flask forms definitions """

import datetime as dt
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, EmailField, IntegerField, FieldList, Form, FormField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange

try:
    from app.packages import settings
except ModuleNotFoundError:
    from packages import settings


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


class AddCategoryBookForm(FlaskForm):
    """
    Description: the add category book FlaskForm form.
    """
    title = StringField(
        label="CATEGORIE", validators=[DataRequired(), Length(min=3, max=50)]
    )


class UpdateeBookCategoryForm(FlaskForm):
    """
    Description: the update category book FlaskForm form.
    """
    title = StringField(
        label="CATEGORIE", validators=[DataRequired(), Length(min=3, max=50)]
    )


class BookCategory(Form):
    """
    Description: the field list for select a book category.
    """
    categories_tupple_list = []
    for category in settings.BOOKS_CATEGORIES:
        categories_tupple_list.append((f'{category.lower()}', f'{category.upper()}'))
    intitule = SelectField("CATEGORIE", choices=categories_tupple_list)


class BookForm(FlaskForm):
    """
    Description: the book FlaskForm form.
    """
    max_year = dt.date.today().year
    def validate_category(form, field):
        if field.data not in settings.BOOKS_CATEGORIES:
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
    categories = FieldList(FormField(BookCategory), min_entries=1, max_entries=1)
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
    def validate_category(form, field):
        if field.data not in settings.BOOKS_CATEGORIES:
            raise ValidationError("Catégorie livre non prévue")

    title = StringField(
        label="TITRE", validators=[DataRequired(), Length(min=3, max=80)]
    )
    summary = StringField(
        label="SOUS-TITRE", validators=[DataRequired(), Length(min=3, max=350)]
    )
    content = TextAreaField(
        label="DESCRIPTION", validators=[DataRequired(), Length(max=2500)]
    )
    categories = FieldList(FormField(BookCategory), min_entries=1, max_entries=1)
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
