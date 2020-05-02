import os
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, \
RoleMixin, current_user, login_required
from flask_security.forms import RegisterForm
from wtforms import StringField, TextAreaField
from flask_wtf import FlaskForm

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['DEBUG'] = True
APP.config['SECRET_KEY'] = os.urandom(300)
APP.config['SECURITY_REGISTERABLE'] = True
APP.config['SECURITY_PASSWORD_SALT'] = 'ThisShouldBeAProperRandomString'
APP.config['SECURITY_SEND_REGISTER_EMAIL'] = False

DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)


roles_users = DB.Table('roles_users',
                       DB.Column('user_id', DB.Integer(), DB.ForeignKey('user.id')),
                       DB.Column('role_id', DB.Integer(), DB.ForeignKey('role.id')))


class Role(DB.Model, RoleMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(80), unique=True)
    description = DB.Column(DB.String(250))


class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    email = DB.Column(DB.String(255), unique=True)
    password = DB.Column(DB.String(255))
    name = DB.Column(DB.String(255))
    username = DB.Column(DB.String(255), unique=True)
    active = DB.Column(DB.Boolean())
    confirmed_at = DB.Column(DB.DateTime())
    roles = DB.relationship('Role', secondary=roles_users,
                            backref=DB.backref('users', lazy='dynamic'))
    replies = DB.relationship('Reply', backref='user', lazy='dynamic')


class Thread(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(30))
    description = DB.Column(DB.String(200))
    date_created = DB.Column(DB.DateTime())
    replies = DB.relationship('Reply', backref='thread', lazy='dynamic')

    def last_post_date(self):
        last_reply = Reply.query.filter_by(thread_id=self.id).order_by(Reply.id.desc()).first()

        if last_reply:
            return last_reply.date_created

        return self.date_created


class Reply(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    thread_id = DB.Column(DB.Integer, DB.ForeignKey('thread.id'))
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    message = DB.Column(DB.String(200))
    date_created = DB.Column(DB.DateTime())


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Name')
    username = StringField('Username')


class NewThread(FlaskForm):
    title = StringField('Title')
    description = StringField('Description')


class NewReply(FlaskForm):
    message = TextAreaField('Message')


USER_DATASTORE = SQLAlchemyUserDatastore(DB, User, Role)
SECURITY = Security(APP, USER_DATASTORE, register_form=ExtendedRegisterForm)


@APP.route('/', methods=['GET', 'POST'])
def index():
    form = NewThread()

    if form.validate_on_submit():
        new_thread = Thread(title=form.title.data, description=form.description.data,
                            date_created=datetime.now())
        DB.session.add(new_thread)
        DB.session.commit()

    threads = Thread.query.all()

    return render_template('index.html', form=form, threads=threads)


@APP.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@APP.route('/thread/<thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    form = NewReply()
    thread = Thread.query.get(int(thread_id))

    if form.validate_on_submit():
        reply = Reply(user_id=current_user.id, message=form.message.data,
                      date_created=datetime.now())
        thread.replies.append(reply)
        DB.session.commit()

    replies = Reply.query.filter_by(thread_id=thread_id).all()

    return render_template('thread.html', thread=thread, form=form, replies=replies)


if __name__ == '__main__':
    APP.run()
