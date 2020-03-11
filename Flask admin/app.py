from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
from flask_admin.contrib.fileadmin import FileAdmin
from os.path import dirname, join
from flask_login import LoginManager, UserMixin, login_user, logout_user, \
current_user

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_db.db'
APP.config['SECRET_KEY'] = 'MySecretKey'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

DB = SQLAlchemy(APP)
ADMIN = Admin(APP, template_mode='bootstrap3')
LOGIN_MANAGER = LoginManager(APP)

@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(20))
    password = DB.Column(DB.String(50))
    age = DB.Column(DB.Integer)
    birthday = DB.Column(DB.DateTime)
    comments = DB.relationship('Comment', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Comment(DB.Model):
    id  = DB.Column(DB.Integer, primary_key=True)
    comment_text = DB.Column(DB.String(200))
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Comment {self.id}>'


class UserView(ModelView):
    column_exclude_list = []
    column_display_pk = True
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    create_modal = True

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)

    inline_models = [Comment]

    # Hides from the bar
    def is_accessible(self):
        return current_user.is_authenticated

    # Blocks direct URL
    def inaccessible_callback(self, name, **kwargs):
        return 'You can not access this!'


ADMIN.add_view(UserView(User, DB.session))
ADMIN.add_view(ModelView(Comment, DB.session))

path = join(dirname(__file__), 'uploads')
ADMIN.add_view(FileAdmin(path, '/uploads', name='Uploads'))


@APP.route('/login')
def login():
    user = User.query.filter_by(id=1).first()
    login_user(user)
    return redirect(url_for('admin.index'))


@APP.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.index'))


if __name__ == '__main__':
    APP.run(debug=True)
