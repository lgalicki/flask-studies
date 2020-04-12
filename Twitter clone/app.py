import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager


APP = Flask(__name__)

PHOTOS = UploadSet('photos', IMAGES)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///engage.db'
APP.config['DEBUG'] = True
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SECRET_KEY'] = os.urandom(30)
APP.config['UPLOADED_PHOTOS_DEST'] = 'images'

configure_uploads(APP, PHOTOS)

DB = SQLAlchemy(APP)
LOGIN_MANAGER = LoginManager(APP)
LOGIN_MANAGER.login_view = 'login' # Where to send unlogged users to.
MIGRATE = Migrate(APP, DB)


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


@APP.template_filter('time_since')
def time_since(delta):
    seconds = delta.total_seconds()

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if days > 0:
        return f'{int(days)}d'
    elif hours > 0:
        return f'{int(hours)}h'
    elif minutes > 0:
        return f'{int(minutes)}m'
    else:
        return f'{int(seconds)}s'


from views import *


MANAGER = Manager(APP)
MANAGER.add_command('DB', MigrateCommand)


if __name__ == '__main__':
    MANAGER.run()
