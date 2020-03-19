from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, login_required, current_user, roles_accepted, http_auth_required
from flask_mail import Mail
from flask_security.forms import ConfirmRegisterForm, NextFormMixin
from wtforms import StringField, IntegerField

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'ASecretKeyThatShouldNotBeLikeThis.ShoulDBeRandom'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///security.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['SECURITY_REGISTERABLE'] = True
APP.config['SECURITY_PASSWORD_SALT'] = 'ShouldBeARandomStringToo!'
APP.config['SECURITY_SEND_REGISTER_EMAIL'] = True
APP.config['SECURITY_CONFIRMABLE'] = True
APP.config['SECURITY_RECOVERABLE'] = True
APP.config['SECURITY_CHANGEABLE'] = True
APP.config['SECURITY_EMAIL_SUBJECT_REGISTER'] = "This subject has been customized!"
#APP.config['SECURITY_EMAIL_SENDER'] = 'doNotAnswer@gmail.com'
APP.config.from_pyfile('mail.cfg')

DB = SQLAlchemy(APP)
MAIL = Mail(APP)

roles_users = DB.Table('roles_users',
        DB.Column('user_id', DB.Integer(), DB.ForeignKey('user.id')),
        DB.Column('role_id', DB.Integer(), DB.ForeignKey('role.id')))

class Role(DB.Model, RoleMixin):
    id = DB.Column(DB.Integer(), primary_key=True)
    name = DB.Column(DB.String(80), unique=True)
    description = DB.Column(DB.String(255))

class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(255), unique=True)
    password = DB.Column(DB.String(255))
    name = DB.Column(DB.String(255))
    age = DB.Column(DB.Integer)
    active = DB.Column(DB.Boolean())
    confirmed_at = DB.Column(DB.DateTime())
    roles = DB.relationship('Role', secondary=roles_users,
                            backref=DB.backref('users', lazy='dynamic'))


class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    name = StringField('Name')
    age = IntegerField('Age')


USER_DATASTORE = SQLAlchemyUserDatastore(DB, User, Role)
SECURITY = Security(APP, USER_DATASTORE, confirm_register_form=ExtendedConfirmRegisterForm)


@APP.route('/')
def index():
    return 'This is an unprotected page'


@APP.route('/protected')
@login_required
def protected():
    return f'This is a <b>protected</b> page and your email is {current_user.email}'


@APP.route('/roleprotected')
@roles_accepted('admin')
def roleprotected():
    return 'Only admins can access this route'


@APP.route('/create_n_assign_admin')
@login_required
def create_n_assign_admin():
    admin_role = USER_DATASTORE.find_or_create_role('admin')
    USER_DATASTORE.add_role_to_user(current_user, admin_role)
    DB.session.commit()
    return f"You are now admin, {current_user.email}."


@APP.route('/http_auth')
@http_auth_required
def http_auth():
    return 'This is a page protected by basic HTTP auth.'


if __name__ == '__main__':
    APP.run(debug=True)
