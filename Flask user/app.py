'''
Login through route /user/sign-in.
Register through /user/register.
Logout through /user/sign-out.
For profile access /user/profile.
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, SQLAlchemyAdapter, login_required, \
current_user
from flask_mail import Mail

APP = Flask(__name__)

APP.config['SECRET_KEY'] = 'RandomStringThatShouldBeAutomaticallyGenerated'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
APP.config['CSRF_ENABLED'] = True
APP.config['USER_ENABLE_EMAIL'] = True
APP.config['USER_APP_NAME'] = "Júpiter's app"
APP.config['USER_AFTER_REGISTER_ENDPOINT'] = 'user.login'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config.from_pyfile('mail.cfg')


DB = SQLAlchemy(APP)
MAIL = Mail(APP)


class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(50), nullable=False, unique=True)
    password = DB.Column(DB.String(255), nullable=False, server_default='')
    active = DB.Column(DB.Boolean, nullable=False, server_default='0')
    email = DB.Column(DB.String(255), nullable=False, unique=True)
    confirmed_at = DB.Column(DB.DateTime())


DB_ADAPTER = SQLAlchemyAdapter(DB, User)
USER_MANAGER = UserManager(DB_ADAPTER, APP)


@APP.route('/')
def index():
    return "<h1>There's no need to be logged in to see this page<//h1>"


@APP.route('/protected')
@login_required
def protected():
    return f"<h1>Your registration was confirmed at {current_user.confirmed_at} " \
           f"through {current_user.email}, {current_user.username}"


if __name__ == '__main__':
    APP.run(debug=True)
