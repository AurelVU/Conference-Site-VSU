# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from operator import attrgetter

from config import UPLOAD_DIR


from flask import render_template, redirect, url_for, flash, request, send_from_directory, session
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user

from flasgger import Swagger

from init import application, db, socketio



swagger_template = {
    # Other settings

    'securityDefinitions': {
        'basicAuth': {
            'type': 'basic'
        }
    },

    # Other settings
}
Swagger(application,  template=swagger_template)
import events

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
    """
            Получение главной страницы
            Call this api passing a language name and get back its features
            ---
            tags:
              - Awesomeness Language API
            responses:
              200:
                description: html страница
                content:
                    html страница

            """
    _news = models.New.query.order_by(models.New.timestamp.desc()).limit(3).all()
    news = []
    for n in _news:
        news.append({'data': n.timestamp.strftime("%d.%m.%Y"), 'title': n.title, 'text': n.text })
    return render_template("index.html", news=news,
                           title='Главная', index='active')

@application.route('/contact')
def contact():
    """
        Получение контактной информации
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            content:
                html страница

    """
    return render_template("contact.html",
                           title = 'Контакты', contact='active')

@application.route('/download')
def download():
    """
        Получение списка сборников
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            content:
                html страница

        """
    compitarions = models.Compilation.query.all()
    files = {}
    for c in compitarions:
        file = models.File.query.filter_by(id=c.file).first()
        files[c] = file
    return render_template("download.html",
                           title = 'Архив', compitarions=compitarions, files=files ,download='active')




@application.route('/news')
def news():
    """
    Получение актуальных новостей
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        content:
            html страница

    """
    _news = models.New.query.order_by(models.New.timestamp.desc()).all()
    news = []
    for n in _news:
        news.append({'data': n.timestamp.strftime("%d.%m.%Y %H:%M:%S"), 'title': n.title, 'text': n.text, 'id': n.id })
    return render_template("news.html", newss=news,
                           title = 'Новости', news='active')

@application.route('/delete_news', methods=['POST'])
@login_required
def delete_news():
    """
        Удаление новостей
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    if current_user.id == 2:
        id = request.form['id']
        models.New.query.filter_by(id=id).delete()
        db.session.commit()
        return  redirect(url_for('news'))

@application.route('/paper')
def paper():
    return render_template("paper.html",
                           title = 'Сборник', paper='active')

@application.route('/login', methods=['GET', 'POST'])
def login():
    """
            Логин
            Call this api passing a language name and get back its features
            ---
            tags:
              - Awesomeness Language API
            responses:
              200:
                description: html страница
                parameters:
                  - name: "id"
                    in: "delete_news"
                    description: "ID новости"
                    required: true
                    type: "integer"
                    format: "int64"
                content:
                    html страница

    """
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
            Выход
            Call this api passing a language name and get back its features
            ---
            tags:
              - Awesomeness Language API
            responses:
              200:
                description: html страница
                parameters:
                  - name: "id"
                    in: "delete_news"
                    description: "ID новости"
                    required: true
                    type: "integer"
                    format: "int64"
                content:
                    html страница

    """
    logout_user()
    return redirect(url_for('index'))

@application.route('/add_compilation', methods=['GET', 'POST'])
@login_required
def add_compilation():
    """
                Добавить сборник
                Call this api passing a language name and get back its features
                ---
                tags:
                  - Awesomeness Language API
                responses:
                  200:
                    description: html страница
                    parameters:
                      - name: "id"
                        in: "delete_news"
                        description: "ID новости"
                        required: true
                        type: "integer"
                        format: "int64"
                    content:
                        html страница

        """
    form = AddCompilation()
    if current_user.role == 2:
        if form.validate_on_submit():
            name = form.name.data
            current_file = form.file.data
            image = form.ico.data
            file = models.File.upload(current_file, image=True, fileimage=image)

            db.session.add(file)
            db.session.commit()


            file = models.File.query.filter(models.File.drive_file_id==file.drive_file_id).first()
            compilation = models.Compilation(file=file.id, name=name)
            db.session.add(compilation)
            db.session.commit()
            return redirect(url_for('download'))
        else:
            return render_template('add_compilation.html', form=form)
    return 'Ошибка доступа'


@application.route('/change_stat', methods=['POST'])
@login_required
def change_stat():
    """
                Сменить статус статьи
                Call this api passing a language name and get back its features
                ---
                tags:
                  - Awesomeness Language API
                responses:
                  200:
                    description: html страница
                    parameters:
                      - name: "id"
                        in: "delete_news"
                        description: "ID новости"
                        required: true
                        type: "integer"
                        format: "int64"
                    content:
                        html страница

        """
    statuses = models.Status.query.all()
    st = [(i.id, i.name) for i in statuses]
    ChangeArticleStatus.setStatuses(st)
    form = ChangeArticleStatus()
    if current_user.role == 2 or current_user.role == 3:
        if form.submit.data:
            id_art = int(form.id.data)
            stat = int(form.stat.data)
            models.Article.query.filter_by(id=id_art).update({'stat': stat})
            db.session.commit()
            return '<script>document.location.href = document.referrer</script>'




@application.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    """
        Добавить новость
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
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
            return render_template('add_news.html', form=form)
    return 'Ошибка доступа'


@application.route('/article', methods=['GET', 'POST'])
@login_required
def article():
    """
        Статьи пользователей
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    updform = UpdateArticle()
    form = UploadArticle()
    fromDate = datetime.now() - timedelta(days=365)
    na_rass = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=1).count()
    otclon = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=2).count()
    prin = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=3).count()
    alll = models.Article.query.filter(models.Article.timestamp >= fromDate).count()
    if form.submit.data:
        block = models.BlockUser.query.filter_by(id_user=current_user.id).first()
        if (block is None) or not (block.block_article):
            if block is not None and (block.block_file):
                return 'Блокировка загрузки файлов'
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
            return 'Блокировка добавления статей'
    else:
        articles = models.Article.query.join(models.File, (models.File.id == models.Article.file)).all()
        files = models.File.query.filter(models.File.owner == current_user.id).all()
        statuses = models.Status.query.all()
        st = [(i.id, i.name) for i in statuses]
        ChangeArticleStatus.setStatuses(st)
        forms = {}
        articlesss = []
        st = models.Status.query.all()
        statuses = {}
        for s in st:
            statuses[s.id] = s.name
        for art in articles:
            forms[art.id] = ChangeArticleStatus(id=art.id, stat=art.stat)
            for f in files:
                if art.file == f.id:
                    articlesss.append({'article': art, 'file': f, 'owner' : current_user.username, 'owner_id' : current_user.id, 'id':art.id, 'stat_id': art.stat, 'stat':statuses[art.stat], 'timestamp' : art.timestamp.strftime("%d.%m.%Y %H:%M:%S") })

        return render_template('articles.html', form=form, updform=updform, forms=forms, na_rass=na_rass ,otclon=otclon, prin=prin, all=alll,  articles=articlesss)


@application.route('/articles', methods=['GET', 'POST'])
@login_required
def articles():
    """
        Все статьи
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    if current_user.role == 2 or current_user.role == 3:
        updform = UpdateArticle()
        fromDate = datetime.now() - timedelta(days=365)
        na_rass = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=1).count()
        otclon = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=2).count()
        prin = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=3).count()
        alll = models.Article.query.filter(models.Article.timestamp >= fromDate).count()
        forms={}
        all = {}
        users = User.query.all()
        us = {}
        for i in users:
            us[i.id] = i
        statuses = models.Status.query.all()
        st = [(i.id, i.name) for i in statuses]
        ChangeArticleStatus.setStatuses(st)
        articles = models.Article.query.all()
        files = models.File.query.all()
        articlesss = []
        st = models.Status.query.all()
        statuses = {}
        for s in st:
            statuses[s.id] = s.name
        for art in articles:
            forms[art.id] = ChangeArticleStatus(id=art.id, stat=art.stat)
            for f in files:
                if art.file == f.id:
                    articlesss.append({'article': art, 'file': f, 'owner' : us[f.owner].username, 'owner_id' : us[f.owner].id, 'id':art.id, 'stat_id': art.stat, 'stat':statuses[art.stat], 'timestamp' : art.timestamp.strftime("%d.%m.%Y %H:%M:%S") })

        return render_template('all_articles.html', form=form, updform=updform, forms=forms, na_rass=na_rass ,otclon=otclon, prin=prin, all=alll, articles=articlesss)
    else:
        return 'Ошибка доступа'

@application.route('/user/<username>')
@login_required
def user(username):
    """
        Страница пользователя
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    user = User.query.filter_by(username=username).first_or_404()
    messages = models.Message.query.filter_by(id_to=user.id).join(User, (User.id == models.Message.id_from)).all()
    messages += (models.Message.query.filter_by(id_from=user.id).join(User, (User.id == models.Message.id_to)).order_by(
        models.Message.timestamp.desc()).all())
    posts = []
    users = set()
    messages = sorted(messages, key=attrgetter('timestamp'), reverse=True)
    for m in messages:
        if user.id == m.id_to:
            user_to = user
            user_from = User.query.filter_by(id=m.id_from).first_or_404()
            received = user_from
            if not (user_from.id in users):
                posts.append({'author': user_from, 'recipient': user_to, 'body': m.text,
                              'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})
                users.add(user_from.id)
        else:
            user_to = User.query.filter_by(id=m.id_to).first_or_404()
            user_from = user
            received = user_to
            if not (user_to.id in users):
                posts.append({'author': user_from, 'recipient': user_to, 'body': m.text,
                              'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})
                users.add(user_to.id)

    return render_template('user.html', user=user, posts=posts)

@application.route('/register', methods=['GET', 'POST'])
def register():
    """
        Страница регистрации
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница
    """
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
    """
    Скачать файл
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    remove_folder_contents(UPLOAD_DIR)
    fl = models.File.query.filter_by(drive_file_id=file_id).first_or_404()
    file_path = fl.download()

    return send_from_directory(directory=UPLOAD_DIR, filename=fl.name)

@application.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
        Изменить профиль
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.second_name.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.second_name.data = current_user.last_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@application.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Изменить пароль
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    form = EditPasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Your changes have been saved.')
        else:
            flash('Password is not correct')
        return redirect(url_for('change_password'))
    return render_template('change_password.html', title='Change Password',
                           form=form)

@application.route('/update_article', methods=['POST'])
@login_required
def update_article():
    """
        Обновить файл у статьи
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        security:
           - basicAuth
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    form = UpdateArticle()
    block = models.BlockUser.query.filter_by(id_user=current_user.id).first()
    if block is not None and (block.block_file):
        return 'Блокировка загрузки файлов'
    id = form.id.data
    current_file = form.file.data
    file = models.File.upload(current_file)
    db.session.add(file)
    idfile = models.File.query.filter_by(drive_file_id=file.drive_file_id).first_or_404()
    article = models.Article.query.filter_by(id=id).first()
    article.file = idfile.id
    db.session.commit()
    return '<script>document.location.href = document.referrer</script>'

@application.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    """
    Чат
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    user = User.query.filter_by(username=current_user.username).first_or_404()
    messages = models.Message.query.filter_by(id_to=user.id).join(User, (User.id == models.Message.id_from)).all()
    messages += (models.Message.query.filter_by(id_from=user.id).join(User, (User.id == models.Message.id_to)).order_by(
        models.Message.timestamp.desc()).all())
    posts = []
    msgs = []
    users = set()
    received = None
    messages = sorted(messages, key=attrgetter('timestamp'), reverse = True)
    for m in messages:
        if user.id == m.id_to:
            user_to = user
            user_from = User.query.filter_by(id=m.id_from).first_or_404()
            received = user_from
            if not(user_from.id in users):
                posts.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})
                users.add(user_from.id)
        else:
            user_to = User.query.filter_by(id=m.id_to).first_or_404()
            user_from = user
            received = user_to
            if not (user_to.id in users):
                posts.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})
                users.add(user_to.id)
    id_to = ''

    if request.args.get('id_to'):
        id_to = int(request.args['id_to'])
        session['room'] = str(min(current_user.id, id_to)) + '_' + str(max(current_user.id, id_to))
        messages2 = models.Message.query.filter_by(id_to=user.id).filter_by(id_from=id_to).join(User, (
                    User.id == models.Message.id_from)).all()
        messages2 += (models.Message.query.filter_by(id_from=user.id).filter_by(id_to=id_to).join(User, (
                    User.id == models.Message.id_to)).order_by(
            models.Message.timestamp.desc()).all())
        messages2 = sorted(messages2, key=attrgetter('timestamp'))
        flag = False
        for m in messages2:
            if user.id == m.id_to:
                user_to = user
                user_from = User.query.filter_by(id=m.id_from).first_or_404()
                received = user_from
                if received.id == int(id_to):
                    flag = True
                msgs.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})
            else:
                user_to = User.query.filter_by(id=m.id_to).first_or_404()
                user_from = user
                received = user_to
                if received.id == int(id_to):
                    flag = True
                msgs.append({'author': user_from, 'recipient': user_to, 'body': m.text, 'timestamp': m.timestamp.strftime("%d.%m.%Y %H:%M:%S")})

        if not flag:
            to = User.query.filter_by(id=int(id_to)).first_or_404()
            posts.append({'author': user, 'recipient': to, 'body': '', 'timestamp': ''})

    users = User.query.all()
    users_logins = [(i.username, i.username) for i in users]
    SendMessage.setLogins(users_logins)
    form = SendMessage()
    return render_template('send_message.html', title='Отправить сообщение', posts=posts, received=received, msgs=msgs, form=form, id_to=id_to)

@application.route('/change_role', methods=['POST'])
@login_required
def change_role():
    """
    Изменить роль
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description: html страница
        parameters:
          - name: "id"
            in: "delete_news"
            description: "ID новости"
            required: true
            type: "integer"
            format: "int64"
        content:
            html страница

    """
    if current_user.role == 2:
        bm = True if request.form.get('bm') else False
        ba = True if request.form.get('ba') else False
        bf = True if request.form.get('bf') else False
        id = request.form['id']
        block = models.BlockUser.query.filter_by(id_user=id).first()
        if block:
            if not((not(bm)) and ((not(ba)) and (not(bf)))):
                block.block_file = bf
                block.block_article = ba
                block.block_message = bm
            else:
                models.BlockUser.query.filter_by(id_user=id).delete()
        else:
            bl = models.BlockUser(block_message=bm, block_article=ba, block_file=bf, id_user=id)
            db.session.add(bl)
        db.session.commit()
        return redirect(url_for('users'))
    else:
        return 'Ошибка доступа'

@application.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    """
        Список пользователей
        Call this api passing a language name and get back its features
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description: html страница
            parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
            content:
                html страница

        """
    users = []
    if request.args.get('search'):
        string = request.args['search']
        users = User.query.filter(User.username.like(string + '%')).all()
    else:
        users = User.query.all()
    roles = models.Role.query.all()
    current_role = [(i.id, i.name) for i in roles]
    ChangeUser.setRoles(current_role)

    rolesss = {}
    forms = {}
    blockss = dict()
    for u in users:
        blockss[u.id] = dict()
        block = models.BlockUser.query.filter_by(id_user=u.id).first()
        if block:
            blockss[u.id]['bm'] = block.block_message
            blockss[u.id]['ba'] = block.block_article
            blockss[u.id]['bf'] = block.block_file
        else:
            blockss[u.id]['bm'] = False
            blockss[u.id]['ba'] = False
            blockss[u.id]['bf'] = False
        form = ChangeUser(user_id=u.id, role=u.role)
        #form.id.data = u.id
        #form.role.default = u.role
        forms[u.id] = form
    for r in roles: #2 - admin, 1 - user, 3 - changer
        rolesss[r.id] = r.name
    if form.submit.data:
        if current_user.role == 2:
            id_user = int(form.user_id.data)
            role = int(form.role.data[0])
            User.query.filter_by(id=id_user).update({'role': role})
            db.session.commit()

    return render_template('users.html', title='Смена роли', users=users, blocks=blockss, forms=forms, roles=rolesss)

if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0')
    #application.run()

