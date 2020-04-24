import os
from _md5 import md5
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user

import googledrive
from init import db, login, application
from config import UPLOAD_DIR

@application.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer, db.ForeignKey('role.id'))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    drive_folder_id = db.Column(db.String(512))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def load_user(id):
        ...

    def set_role(self, role):
        ...

    def add_news(self, news):
        ...

    def add_compilation(file_id, compilation_name):
        ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.name)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    drive_file_id = db.Column(db.String(512))

    def download(self):
        return googledrive.download_file(self.name, self.drive_file_id)

    def upload(file):
        savepath = os.path.join(UPLOAD_DIR, file.filename)
        file.save(savepath)
        drive_id_file = googledrive.upload_file(current_user.drive_folder_id, UPLOAD_DIR, file.filename)
        os.remove(savepath)
        return File(name=file.filename, owner=current_user.id, drive_file_id=drive_id_file)

    def __repr__(self):
        return '<File {}>'.format(self.name)

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Status {}>'.format(self.name)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.Integer, db.ForeignKey('file.id'))
    name = db.Column(db.String(64), index=True)
    stat = db.Column(db.Integer, db.ForeignKey('status.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def add_article(file_id, article_name):
        ...

    def change_status(self, status_id):
        ...

    def __repr__(self):
        return '<Article {}>'.format(self.name)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_from = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    text = db.Column(db.String(5000))

    def get_all_messages_from_user(user_id):
        ...

    def get_all_messages_to_user(user_id):
        ...

    def send_message(user_id_from, user_id_to):
        ...

    def get_all_mes_from_conversation(user_id_from, user_id_to):
        ...

    def get_all_mes_to_conversation(user_id_frim, user_id_to):
        ...

    def __repr__(self):
        return '<Message {}>'.format(self.text)

class Compilation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))
    file = db.Column(db.Integer, db.ForeignKey('file.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Compilation {}>'.format(self.text)

class BlockUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    block_message = db.Column(db.Boolean)
    block_article = db.Column(db.Boolean)
    block_file = db.Column(db.Boolean)

    def add_blockuser(user_id, block_message, block_article, block_file):
        return BlockUser(id_user=user_id, block_message=block_message, block_article=block_article, block_file=block_file)

    def check_user(user_id):
        block = BlockUser.query.filter_by(id_user=user_id).first
        if block == None:
            return False, False, False
        else:
            return block.block_message, block.block_article, block.block_file

    def delete_block(user_id, block_message, block_article, block_file):
        ...


class New(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    text = db.Column(db.String(5000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)