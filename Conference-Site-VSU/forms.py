from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import * # BooleanField, StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo, Length

from models import User


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(),  Length(min=3, max=64)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=20)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('email', validators=[Email(), DataRequired()])
    first_name = StringField('Имя', validators=[Length(min=4, max=20)])
    second_name = StringField('Фамилия', validators=[Length(min=2, max=30)])
    password = PasswordField('Пароль', validators=[DataRequired(),  Length(min=6, max=20)])
    password_2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Подтвердить')

class EditPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')

class UploadArticle(FlaskForm):
    name = StringField('Название статьи', validators=[DataRequired()])
    file = FileField('Файл вашей работы', validators=[DataRequired(), FileRequired(), FileAllowed(['pdf', 'docx', 'rtx'], 'Только документы формата pdf, docx, rtx')])
    submit = SubmitField('Отправить')

class SendMessage(FlaskForm):
    login_to = SelectMultipleField('Адресат')
    message = TextAreaField('Сообщение', validators=[Length(min=0, max=5000)])
    submit = SubmitField('Отправить')
    def setLogins(users):
        SendMessage.login_to = SelectMultipleField('Адресат', choices=users, validators=[DataRequired()])
        SendMessage.message = TextAreaField('Сообщение', validators=[Length(min=0, max=5000)])
        SendMessage.submit = SubmitField('Отправить')

class ChangeUser(FlaskForm):
    def setRoles(roles):
        ChangeUser.role = SelectMultipleField('Роль', validators=[DataRequired()], choices=roles)
        ChangeUser.submit = SubmitField('Отправить')
        ChangeUser.id = HiddenField('id')


class AddNews(FlaskForm):
    title = StringField('Заголовок')
    text = StringField('Текст новости')
    submit = SubmitField('Отправить')