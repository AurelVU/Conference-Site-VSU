import os

from flask import Flask, render_template, redirect, url_for, flash, request
from flask.views import View
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
import routes, models
from forms import *
bootstrap = Bootstrap(app)

UPLOAD_DIR =  os.path.join(os.path.abspath(os.path.dirname(__file__)), 'upload')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Главная')

@app.route('/contact')
def contact():
    return render_template("contact.html",
        title = 'Контакты')

@app.route('/download')
def download():
    return render_template("download.html",
        title = 'Архив')

@app.route('/news')
def news():
    return render_template("news.html",
        title = 'Новости')

@app.route('/paper')
def paper():
    return render_template("paper.html",
        title = 'Сборник')

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/article', methods=['GET', 'POST'])
@login_required
def article():
    form = UploadArticle()
    if form.validate_on_submit():
        current_file = form.file.data
        if not os.path.exists(os.path.join(UPLOAD_DIR, current_user.username)) :
            os.mkdir(os.path.join(UPLOAD_DIR, current_user.username))
        savepath = os.path.join(os.path.join(UPLOAD_DIR, current_user.username), current_file.filename)
        current_file.save(savepath)
        file = models.File(name=current_file.filename, path=savepath, owner=current_user.id)
        db.session.add(file)
        db.session.commit()
        idfile = models.File.query.filter_by(path=savepath).first_or_404()
        article = models.Article(file=idfile.id, name=form.name.data, stat=1)
        db.session.add(article)
        db.session.commit()
        #file = models.File(name=, path=, owner=current_user.id)
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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    messages = models.Message.query.filter_by(id_to=user.id).join(User, (User.id == models.Message.id_from)).all()
    messages += (models.Message.query.filter_by(id_from=user.id).join(User, (User.id == models.Message.id_to)).order_by(models.Message.timestamp.desc()).all())
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=1)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')

        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
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

@app.route('/send_message', methods=['GET', 'POST'])
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


@app.route('/change_role', methods=['GET', 'POST'])
@login_required
def change_role():
    users = User.query.all()
    roles = models.Role.query.all()
    current_role = [(i.id, i.name) for i in roles]
    ChangeUser.setRoles(current_role)
    form = ChangeUser()
    rolesss = {}
    for r in roles: #1 - admin, 2 - user, 3 - changer
        rolesss[r.id] = r.name
    if form.submit.data:
        if current_user.role == 1:
            id_user = int(form.id.data)
            role = int(form.role.data[0])
            User.query.filter_by(id=id_user).update({'role': role})
            db.session.commit()

    return render_template('users.html', title='Смена роли', users=users, form=form, roles=rolesss)

if __name__ == '__main__':
    app.run()
