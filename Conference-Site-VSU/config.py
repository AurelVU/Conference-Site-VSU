import os
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_DIR =  os.path.join(os.path.abspath(os.path.dirname(__file__)), 'upload')

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'Conference-Site-VSU/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False