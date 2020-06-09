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

def validate_space(form, username):
    if ' ' in username.data:
        raise ValidationError('Пробел - недопустимый символ')

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), validate_space])
    email = StringField('email', validators=[Email(), DataRequired()])
    first_name = StringField('Имя', validators=[Length(min=4, max=20)])
    second_name = StringField('Фамилия', validators=[Length(min=2, max=30)])
    password = PasswordField('Пароль', validators=[DataRequired(),  Length(min=6, max=20)])
    password_2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другое имя пользователя.')



    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста введите другую электронную почту.')


class EditProfileForm(FlaskForm):
    email = StringField('email', validators=[Email(), DataRequired()])
    first_name = StringField('Имя', validators=[Length(min=4, max=20)])
    second_name = StringField('Фамилия', validators=[Length(min=2, max=30)])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Подтвердить')

class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password_2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')

class UploadArticle(FlaskForm):
    name = StringField(validators=[DataRequired()])
    file = FileField(validators=[DataRequired(), FileRequired(), FileAllowed(['pdf', 'docx', 'rtx'], 'Только документы формата pdf, docx, rtx')])
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
        ChangeUser.role = SelectField('Роль', validators=[DataRequired()], choices=roles)
        ChangeUser.submit = SubmitField('Отправить')
        ChangeUser.user_id = HiddenField('id')


class AddNews(FlaskForm):
    title = StringField('Заголовок:', validators=[Length(min=0, max=250)])
    text = TextAreaField('Текст новости:', validators=[Length(min=0, max=5000)])
    submit = SubmitField('Отправить')

class AddCompilation(FlaskForm):
    name = StringField('Введите название сборника', validators=[DataRequired()])
    file = FileField(validators=[DataRequired(), FileRequired(), FileAllowed(['pdf'], 'Только документы формата pdf')])
    ico = FileField(validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'],
                    'Только "jpg", "jpeg" и "png" файлы поддерживаются')])
    submit = SubmitField('Отправить')

class ChangeArticleStatus(FlaskForm):
    def setStatuses(statuses):
        ChangeArticleStatus.stat = SelectField('Статус', validators=[DataRequired()], choices=statuses)
        ChangeArticleStatus.submit = SubmitField('Отправить')
        ChangeArticleStatus.id = HiddenField('id')


class UpdateArticle(FlaskForm):
    id = HiddenField('id')
    file = FileField(validators=[DataRequired(), FileRequired(), FileAllowed(['pdf', 'docx', 'rtx'], 'Только документы формата pdf, docx, rtx')])
    submit = SubmitField('Отправить')
