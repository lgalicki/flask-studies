from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, session, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, \
    current_user, logout_user
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'ThisIsASecret'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['USER_SESSION_FOR_NEXT'] = True # This redirects to previous page vefore loging in. Doesn't seem to work though.

LOGIN_MANAGER = LoginManager(APP)
LOGIN_MANAGER.login_view = 'login' # Specifies the route an unlogged user will be routed to if he tries to access a protected route.
LOGIN_MANAGER.login_message = 'Gotta login to access this page!' # Overwriting the default message.

# The two lines below work only if remember me and fresh login are being used.
# They work like the above lines for login view and message
LOGIN_MANAGER.refresh_view = 'login'
LOGIN_MANAGER.needs_refresh_message = 'Gotta login again to access this page!'

DB = SQLAlchemy(APP)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


class User(UserMixin, DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(30), unique=True)


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            return '<h1>User does not exist!</h1>'

        login_user(user)
        # login_user(user, remember=True) #if you wanna keep the session even if the browser is closed. There's a time configuration for this. Check the documentation of the course. Check fresh login too.

        if 'next' in session:
            next_page = session.pop('next')
            if is_safe_url(next_page):
                return redirect(next_page)

        return '<h1>Logged in!</h1>'

    if 'next' in request.args:
        session['next'] = request.args.get('next')

    return render_template('login.html')


@APP.route('/logout')
def logout():
    logout_user()
    return '<h1>Bye-bye!</h1>'


@APP.route('/home')
@login_required
def home():
    return f'<h1>You are in a protected route, {current_user.username}'


if __name__ == '__main__':
    APP.run(debug=True)
