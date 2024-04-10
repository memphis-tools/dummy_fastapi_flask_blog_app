""" The Flask forms definitions """

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, EmailField

# from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length, Email


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


class BookForm(FlaskForm):
    """
    Description: the book FlaskForm form.
    """

    title = StringField(
        label="TITRE", validators=[DataRequired(), Length(min=3, max=80)]
    )
    summary = StringField(
        label="SOUS-TITRE", validators=[DataRequired(), Length(min=3, max=160)]
    )
    content = TextAreaField(
        label="DESCRIPTION", validators=[DataRequired(), Length(max=2500)]
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

    title = StringField(
        label="TITRE", validators=[DataRequired(), Length(min=3, max=80)]
    )
    summary = StringField(
        label="SOUS-TITRE", validators=[DataRequired(), Length(min=3, max=350)]
    )
    content = TextAreaField(
        label="DESCRIPTION", validators=[DataRequired(), Length(max=2500)]
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
