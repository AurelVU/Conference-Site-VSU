# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from operator import attrgetter

from config import UPLOAD_DIR


from flask import render_template, redirect, url_for, flash, request, send_from_directory, session
from flask_bootstrap import Bootstrap
from flask_login import login_user, logout_user, login_required, current_user

from flasgger import Swagger, swag_from

from init import application, db, socketio


Swagger(application)
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
        Главная страница
        Данная страница доступна всем пользователям, попадающим на сайт.
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description:
              Возвращает главную страницу, на которой отображается навбар, заголовок, приветственные сообщения,
              расписание ближайших событий, которое включает в себя календарь и 3 последние новости.
              В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
              а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован),
              или ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
          302:
            description:
              Неизвестная ошибка.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка запроса. Страница не существует.
          500:
            description:
              Выход за пределы массива.
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
        Контактная информация сайта
        Данная страница доступна всем пользователям, попадающим на сайт.
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description:
              Возвращает страницу контактов, на которой отображается навбар, заголовок, сообщение о редакторе сборника,
              список кураторов кафедр с их данными для связи, адрес университета и расположение на карте.
              В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
              а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован),
              или ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
          302:
            description:
              Неизвестная ошибка.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка запроса. Страница не существует.
          500:
            description:
              Выход за пределы массива.
    """
    return render_template("contact.html",
                           title = 'Контакты', contact='active')

@application.route('/download')
def download():
    """
        Архив работ сайта
        Данная страница доступна всем пользователям, попадающим на сайт. У Администратора есть  дополнительная кнопка для перехода на форму добавления сборника.
        ---
        tags:
          - Awesomeness Language API
        responses:
          200:
            description:
              Возвращает страницу Архива работ, на которой отображается навбар, заголовок, список сборников.
              Для Администратора под заголовком располагается кнопка для перехода на страницу добавления сборника.
              В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
              а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован),
              или ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
              В списке сборников отображается иконка сборника, его название и кнопка для скачивания.
          302:
            description:
               Неизвестная ошибка.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка запроса. Страницы не существует.
          500:
            description:
              Выход за пределы массива.
        """
    compitarions = models.Compilation.query.all()
    files = {}
    for c in compitarions:
        file = models.File.query.filter_by(id=c.file).first()
        files[c] = file
    return render_template("download.html",
                           title='Архив', compitarions=compitarions, files=files ,download='active')




@application.route('/news')
def news():
    """
    Актуальные новости сайта
    Данная страница доступна всем пользователям, попадающим на сайт. У Администратора есть дополнительная кнопка для перехода на форму добавления новости и кнопка удаления новости из списка.
    ---
    tags:
      - Awesomeness Language API
    responses:
      200:
        description:
          Возвращает страницу Новостей сайта, на которой отображается навбар, заголовок, список актуальных новостей.
          Для Администратора под заголовком располагается кнопка для перехода на страницу добавления новости.
          В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
          а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован),
          или ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
          В списке новостей отображается название новости, текст, время добавления. Для Администратора на каждой новости из списка
          есть кнопка удаления.
      302:
        description:
          Неизвестная ошибка.
      400:
        description:
          Некорректный запрос.
      404:
        description:
          Ошибка запроса. Страницы не существует.
      500:
        description:
          Выход за пределы массива.

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
        Удалить новость
        POST запрос для передачи данных при удалении новости. Данная страница доступна Администраторам. Перенаправляет на страницу Новостей сайта.
        ---
        tags:
          - Awesomeness Language API
        parameters:
              - name: "id"
                in: "delete_news"
                description: "ID новости"
                required: true
                type: "integer"
                format: "int64"
              - name: submit
                in: formData
                description: "Нажатие кнопки удаления"
                required: true
                type: boolean
                enum:
                  - true
        responses:
          200:
            description:
              Перенаправляет на страницу Новостей сайта, на которой отображается навбар, заголовок, список актуальных новостей без удалённой новости.
              Для Администратора под заголовком располагается кнопка для перехода на страницу добавления новости.
              В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
              а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован),
              или ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
              В списке новостей отображается название новости, текст, время добавления. Удалённая новость отстутствует в нём. Для Администратора на каждой новости из списка
              есть кнопка удаления.
          302:
            description:
              Если пользователь не авторизован, то редирект на страницу Авторизации.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка ввода id новости собеседника. Новость не найдена.
          500:
            description:
              Выход за пределы массива.
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
@swag_from('api/login_get.yml', methods=['GET'])
@swag_from('api/login_post.yml', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.is_submitted():
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
            Выход из системы
            Данная страница доступна авторизированным пользователям. Перенаправляет на Главную страницу сайта.
            ---
            tags:
              - Awesomeness Language API
            responses:
              200:
                description:
                  Возвращает авторизированному пользователю страницу сайта, на которой отображается навбар, заголовок, список актуальных новостей без удалённой новости. Пользователь после этого действия разлогирован.
                  В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
                  а также ссылка на страницу регистрации и URL входа в систему( если пользователь не зарегистрирован или не авторизирован).
              302:
                description:
                  Если пользователь не авторизован, то редирект на страницу Авторизации.
              400:
                description:
                  Некорректный запрос.
              404:
                description:
                  Ошибка запроса.
              500:
                description:
                  Выход за пределы массива.
    """
    logout_user()
    return redirect(url_for('index'))

@application.route('/add_compilation', methods=['GET', 'POST'])
@login_required
@swag_from('api/add_compilation_get.yml', methods=['GET'])
@swag_from('api/add_compilation_post.yml', methods=['POST'])
def add_compilation():
    form = AddCompilation()
    if current_user.role == 2:
        if form.is_submitted():
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
    Изменить статус статьи
    POST запрос для передачи данных при изменения статуса статьи. Данная страница доступна Администраторам и Редакторам. Перенаправляет на страницу Все статьи, если был изменён статус статьи пользователя. Если Администратор или Редактор изменили статус своей статьи на странице Ваши статьи, то будут перенаправлены на неё же.
    ---
    tags:
        - Awesomeness Language API
    parameters:
      - name: stat
        in: formData
        description: Новый статус статьи. 1 - на рассмотрении, 2 - не принята, 3 - принята
        required: true
        type: int
        enum:
          - 1
          - 2
          - 3
      - name: id
        in: formData
        description: id статьи
        required: true
        type: int
      - name: submit
        in: formData
        description: Нажатие кнопки отправить
        required: true
        type: boolean
        enum:
          - true
    responses:
      200:
        description:
          Перенаправляет Администратора или Редактора на страницу Все статьи при изменении статуса статьи пользователя.
          На странице отображается навбар, заголовок, кнопка Назад(перенаправляет на предыдущую страницу сайта), статистику всех статей, список всех поданных статей.
          В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
          а также ссылка на страницу пользователя и URL выхода из системы( если пользователь зарегистрирован и авторизирован).
          Если Администратор или  Редактор изменили статус своей статьи на странице Ваши статьи, то будут перенаправлены на неё же.
          На странице Ваши статьи расположены навбар, заголовок, кнопка Назад, статистика поданых пользователем статей, форма добавления новой стать,
          список всех поданных пользователем статей.
      302:
        description:
          Если пользователь не авторизован, то редирект на страницу Авторизации.
      400:
        description:
          Некорректный запрос.
      404:
        description:
          Ошибка ввода id статьи собеседника. Статья не найдена.
      500:
        description:
          Выход за пределы массива.
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
@swag_from('api/add_news_get.yml', methods=['GET'])
@swag_from('api/add_news_post.yml', methods=['POST'])
def add_news():
    form = AddNews()
    if current_user.role == 2:
        if form.is_submitted():
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
@swag_from('api/article_get.yml', methods=['GET'])
@swag_from('api/article_post.yml', methods=['POST'])
def article():
    updform = UpdateArticle()
    form = UploadArticle()
    fromDate = datetime.now() - timedelta(days=365)
    na_rass = 0
    rrr = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=1).all()
    for r in rrr:
        f = models.File.query.filter_by(id=r.file).first()
        if f.owner == current_user.id:
            na_rass += 1
    otclon = 0
    rrr = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=2).all()
    for r in rrr:
        f = models.File.query.filter_by(id=r.file).first()
        if f.owner == current_user.id:
            otclon += 1
    prin = 0
    rrr = models.Article.query.filter(models.Article.timestamp >= fromDate).filter_by(stat=3).all()
    for r in rrr:
        f = models.File.query.filter_by(id=r.file).first()
        if f.owner == current_user.id:
            prin += 1
    alll = 0
    rrr = models.Article.query.filter(models.Article.timestamp >= fromDate).all()
    for r in rrr:
        f = models.File.query.filter_by(id=r.file).first()
        if f.owner == current_user.id:
            alll += 1
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


@application.route('/articles', methods=['GET'])#, 'POST'])
@login_required
@swag_from('api/articles_get.yml', methods=['GET'])
#@swag_from('api/articles_post.yml', methods=['POST'])
def articles():
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
        Данная страница доступна авторизированным пользователям. У каждого пользователя будут отображаться только его данные.
        ---
        tags:
          - Awesomeness Language API
        parameters:
          - in: path
            name: "username"
            schema:
            type: string
            required: true
            description: username пользователя
        responses:
          200:
            description:
              Возвращает авторизированному пользователю страницу сайта, на которой отображается навбар, заголовок, форму диалогов пользователя слева и форму профиля пользователя.
              В навбаре выводятся ссылки на главную страницу, страницу новостей, сборников, архивов, контактов,
              а также ссылка на страницу профиля и URL выхода из системы( если пользователь зарегистрирован и авторизирован),
              В форме диалогов располагается список диалогов, в каждом из них - иконка собеседника, его имя, дата и время последнего сообщения, сообщение собеседника(если оно было последним), иначе
              иконка пользователя, его последнее сообщение.
              В форме профиля находятся иконка пользователя, его логин, дата и время последнего действия в сети, список доступных ему ссылок-страниц.
              Для обычного пользователя ссылки на страницы Изменение профиля пользователя, Чат, Статьи пользователя, Список пользователей.
              У Редактора и Администратора есть ссылки как у пользователя и добавлена ссылка на страницу Все статьи.
          302:
            description:
              Если пользователь не авторизован, то редирект на страницу Авторизации.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка ввода логина собеседника. Пользователь не найден с введённым логином.
          500:
            description:
              Выход за пределы массива.
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
@swag_from('api/register_get.yml', methods=['GET'])
@swag_from('api/register_post.yml', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.is_submitted():
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
    Данная страница доступна всем пользователям со страницы Арихив работ, только авторизированным пользователям со страниц Статьи пользователя (и Все статьи для Администратора и Редактора)
    ---
    tags:
      - Awesomeness Language API
    parameters:
      - name: file_id
        in: path
        description: ID файла в удаленном хранилище
        required: true
        type: string
    responses:
      200:
        description:
          Осуществляет Скачивание файлов статей или сборника и редирект на ту же страницу, с которй было совершено действие.
          Неавторизованный пользователь может скачать файл только со страницы Архивы работ. Авторизованый , в зависимости от роли, может скачать файл
          со страниц Статьи пользователя и Все статьи(если Администратор или Редактор).
      302:
        description:
          Если пользователь не авторизован и пытается скачать стаьи, то редирект на страницу Авторизации.
      400:
        description:
          Некорректный запрос.
      404:
        description:
          Ошибка id file собеседника. File не найден.
      500:
        description:
          Выход за пределы массива.
    """
    remove_folder_contents(UPLOAD_DIR)
    fl = models.File.query.filter_by(drive_file_id=file_id).first_or_404()
    file_path = fl.download()

    return send_from_directory(directory=UPLOAD_DIR, filename=fl.name)

@application.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@swag_from('api/edit_profile_get.yml', methods=['GET'])
@swag_from('api/edit_profile_post.yml', methods=['POST'])
def edit_profile():
    form = EditProfileForm()
    if form.is_submitted():
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
@swag_from('api/change_password_get.yml', methods=['GET'])
@swag_from('api/change_password_post.yml', methods=['POST'])
def change_password():
    form = EditPasswordForm()
    if form.is_submitted():
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
        POST запрос для передачи данных для обновления статьи. Данная страница доступна только авторизированным пользователям со страниц Статьи пользователя (и Все статьи для Администратора и Редактора)
        ---
        tags:
          - Awesomeness Language API
        consumes:
            - multipart/form-data
        parameters:
          - in: formData
            name: file
            type: file
            description: Прикрепленный файл
          - in: formData
            name: id
            type: string
            description: id статьи
          - name: submit
            in: formData
            description: username
            required: true
            type: boolean
            enum:
              - true
        responses:
          200:
            description:
              Осуществляется обновлени файла на новый после загрузки и редирект на ту же страницу, на которой происходило обновление.
              Данная страница доступна только авторизированным пользователям со страниц Статьи пользователя (и Все статьи для Администратора и Редактора).
          302:
            description:
              Если пользователь не авторизован, то редирект на страницу Авторизации.
          400:
            description:
              Некорректный запрос.
          404:
            description:
              Ошибка ввода id статьи.Статья не найдена с введённым  id.
          500:
            description:
              Выход за пределы массива.
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

@application.route('/send_message', methods=['GET'])#, 'POST'])
@login_required
def send_message():
    """
    Чат
    Данная страница доступна только авторизированным пользователям в их профиле.
    ---
    tags:
      - Awesomeness Language API
    parameters:
      - name: id_to
        in: query
        description: ID собеседника
        type: integer
        format: int64
    responses:
      200:
        description:
          Возвращает страницу Чат, которая имеет навбар для авторизированного пользователя, заголовок "Диалоги", и два блока, один - со списком диалогов, другой - с выводом сообщений выбранного диалога.
          В первом блоке находятся кнопка Назад на предыдущую страницу сайта, список диалогов, в каждом из них - иконка собеседника, его имя, дата и время последнего сообщения, сообщение собеседника(если оно было последним), иначе иконка пользователя, его последнее сообщение.
          Второй блок - это пустая форма для отправки сообщений. С неё невозможно отправить сообщение, пока диалог не выбран.
          Если выбран диалог с пользователем, то во втором блоке отображается список сообщений между собеседниками. Если пользователь зарегистрирован с введённым id, но не было с ним диалога, он создаётся.
      302:
        description:
          Неавторизованный пользователь перенаправляется на страницу Авторизации.
      400:
        description:
          Некорректный запрос.
      404:
        description:
          Ошибка ввода id собеседника. Пользователь не найден с введённым id.
      500:
        description:
          Введённое число выходит за пределы массива.

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
    Изменить разрешения пользователей
    POST запрос для передачи данных при изменения статуса разрешений пользователя. Данная страница доступна только Администраторам со страницы Список пользователей.
    ---
    tags:
        - Awesomeness Language API
    parameters:
      - name: bm
        in: formData
        description: Блокировка сообщений
        required: true
        type: boolean
        enum:
          - true
          - false
      - name: ba
        in: formData
        description: Блокировка загрузки статей
        required: true
        type: boolean
        enum:
          - true
          - false
      - name: bf
        in: formData
        description: Блокировка загрузки файлов
        required: true
        type: boolean
        enum:
          - true
          - false
      - name: id
        in: formData
        description: ID Пользователя
        required: true
        type: int
    responses:
      200:
        description:
          Перенаправляет Администратора на страницу Список пользователей при изменении статуса разрешений, таких как Чат, Файлы, Статьи.
      302:
        description:
          Если неавторизированный пользователь перенаправляется на старницу авторизации.
      404:
        description:
          Ошибка ввода! Пользователь не найден.
      400:
        description:
          Некорректный запрос.
      500:
        description:
          Выход за границы массива.


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
@swag_from('api/users_get.yml', methods=['GET'])
@swag_from('api/users_post.yml', methods=['POST'])
def users():
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
    socketio.run(application)
    #application.run()

