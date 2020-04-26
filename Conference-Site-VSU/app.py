# -*- coding: utf-8 -*-
import os

from config import UPLOAD_DIR

from flask import render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user

from flasgger import Swagger

from init import application, db

Swagger(application)

import models
from forms import *
bootstrap = Bootstrap(application)

import shutil


def remove_folder_contents(path):
    shutil.rmtree(path)
    os.makedirs(path)


import googledrive
@application.route('/')
@application.route('/index')
def index():
    return render_template("index.html",
                           title='Главная', index='active')

@application.route('/contact')
def contact():
    return render_template("contact.html",
                           title = 'Контакты', contact='active')

@application.route('/download')
def download():
    return render_template("download.html",
                           title = 'Архив', download='active')

@application.route('/news')
def news():
    return render_template("news.html",
                           title = 'Новости', news='active')

@application.route('/paper')
def paper():
    return render_template("paper.html",
                           title = 'Сборник', paper='active')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Вход', form=form)

@application.route('/logout')
def logout():
    """
        This is the language awesomeness API
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        parameters:
          - name: language
            in: path
            type: string
            required: true
            description: The language name
          - name: size
            in: query
            type: integer
            description: size of awesomeness
        responses:
          500:
            description: Error The language is not awesome!
          200:
            description: A language with its awesomeness
            schema:
              id: awesome
              properties:
                language:
                  type: string
                  description: The language name
                  default: Lua
                features:
                  type: array
                  description: The awesomeness list
                  items:
                    type: string
                  default: ["perfect", "simple", "lovely"]

        """
    logout_user()
    return redirect(url_for('index'))


@application.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = AddNews()
    if current_user.role == 2:
        if form.validate_on_submit():
            title = form.title.data
            text = form.text.data
            new = models.New(text=text, title=title)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('news'))
        else:
            return render_template('articles.html', form=form)
    return 'Ошибка доступа'


@application.route('/article', methods=['GET', 'POST'])
@login_required
def article():
    form = UploadArticle()
    if form.validate_on_submit():
        current_file = form.file.data
        file = models.File.upload(current_file)
        db.session.add(file)
        db.session.commit()
        idfile = models.File.query.filter_by(drive_file_id=file.drive_file_id).first_or_404()
        article = models.Article(file=idfile.id, name=form.name.data, stat=1)
        db.session.add(article)
        db.session.commit()

        return redirect(url_for('article'))
    else:
        articles = models.Article.query.join(models.File, (models.File.id == models.Article.file)).all()
        files = models.File.query.filter(models.File.owner == current_user.id).all()
        articlesss = []
        st = models.Status.query.all()
        statuses = {}
        for s in st:
            statuses[s.id] = s.name
        for art in articles:
            for f in files:
                if art.file == f.id:
                    articlesss.append({'article': art, 'file': f, 'owner' : current_user.username, 'stat' : statuses[art.stat] })

        return render_template('articles.html', form=form, articles=articlesss)

@application.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    messages = models.Message.query.filter_by(id_to=user.id).join(User, (User.id == models.Message.id_from)).all()
    messages += (models.Message.query.filter_by(id_from=user.id).join(User, (User.id == models.Message.id_to)).order_by(
        models.Message.timestamp.desc()).all())
    posts = []
    for m in messages:
        if user.id == m.id_to:
            user_to = user
            user_from = User.query.filter_by(id=m.id_from).first_or_404()
            posts.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp})
        else:
            user_to = User.query.filter_by(id=m.id_to).first_or_404()
            user_from = user
            posts.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp})
    return render_template('user.html', user=user, posts=posts)

@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        folderid = googledrive.create_new_folder('1y1k_hrwlXcEIJzfpfMv9APl2mAdYUYF6', form.username.data)
        user = User(username=form.username.data, email=form.email.data, role=1, drive_folder_id=folderid,
                    first_name=form.first_name.data, last_name=form.second_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@application.route('/download_file/<file_id>')
def download_file(file_id):
    remove_folder_contents(UPLOAD_DIR)
    fl = models.File.query.filter_by(drive_file_id=file_id).first_or_404()
    file_path = fl.download()

    def generate():
        with open(file_path) as f:
            yield from f
        os.remove(file_path)

    return send_from_directory(directory=UPLOAD_DIR, filename=fl.name)

@application.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@application.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    users = User.query.all()
    users_logins = [(i.username, i.username) for i in users]
    SendMessage.setLogins(users_logins)
    form = SendMessage()
    if form.validate_on_submit():
        for l in form.login_to.data:
            id_to = User.query.filter_by(username=l).first_or_404()
            message = models.Message(id_from=current_user.id, id_to=id_to.id, text=form.message.data)
            db.session.add(message)
        db.session.commit()
        return redirect(url_for('user', username=current_user.username))
    return render_template('send_message.html', title='Отправить сообщение', form=form)


@application.route('/change_role', methods=['GET', 'POST'])
@login_required
def change_role():
    users = User.query.all()
    roles = models.Role.query.all()
    current_role = [(i.id, i.name) for i in roles]
    ChangeUser.setRoles(current_role)
    form = ChangeUser()
    rolesss = {}
    for r in roles: #2 - admin, 1 - user, 3 - changer
        rolesss[r.id] = r.name
    if form.submit.data:
        if current_user.role == 2:
            id_user = int(form.id.data)
            role = int(form.role.data[0])
            User.query.filter_by(id=id_user).update({'role': role})
            db.session.commit()

    return render_template('users.html', title='Смена роли', users=users, form=form, roles=rolesss)

if __name__ == '__main__':
    application.run()
