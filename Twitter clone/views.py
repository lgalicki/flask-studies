from datetime import datetime
from flask import render_template, redirect, url_for, request, abort
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import DB, PHOTOS, APP
from forms import LoginForm, TweetForm, RegisterForm
from models import User, Tweet, followers


@APP.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@APP.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form, current_user=current_user)


@APP.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            return render_template('index.html', form=form, message='Login failed')

        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('profile'))

        return render_template('index.html', form=form, message='Login failed')

    return render_template('index.html', form=form, current_user=current_user)


def list_who_to_watch(user):
    return User.query.filter(User.id != user.id).order_by(DB.func.random()).limit(4).all()


@APP.route('/profile', defaults={'username': None})
@APP.route('/profile/<username>')
@login_required
def profile(username):
    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)

    else:
        user = current_user

    tweets = Tweet.query.filter_by(user=user).order_by(Tweet.date_created.desc()).limit(4).all()
    current_time = datetime.now()
    followed_by = user.followed_by.all()

    display_follow = True
    if current_user == user:
        display_follow = False
    elif user in current_user.following:
            display_follow = False

    who_to_watch = list_who_to_watch(current_user)

    return render_template('profile.html', user=user, tweets=tweets,
                           current_time=current_time, followers=followed_by,
                           display_follow=display_follow,
                           who_to_watch=who_to_watch, current_user=current_user)


@APP.route('/timeline', defaults={'username': None})
@APP.route('/timeline/<username>')
@login_required
def timeline(username):
    form = TweetForm()

    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)
        tweets = Tweet.query.filter_by(user=user).order_by(Tweet.date_created.desc()).all()
        total_tweets = len(tweets)

    else:
        user = current_user
        tweets = Tweet.query.join(followers, (followers.c.followee_id == Tweet.user_id)).filter(followers.c.follower_id == current_user.id).order_by(Tweet.date_created.desc()).all()
        total_tweets = Tweet.query.filter_by(user=user).order_by(Tweet.date_created.desc()).count()

    current_time = datetime.now()

    who_to_watch = list_who_to_watch(current_user)

    return render_template('timeline.html', form=form, tweets=tweets,
                           current_time=current_time, user=user,
                           total_tweets=total_tweets, who_to_watch=who_to_watch,
                           current_user=current_user)


@APP.route('/post_tweet', methods=['POST'])
@login_required
def post_tweet():
    form = TweetForm()

    if form.validate():
        tweet = Tweet(user_id=current_user.id, text=form.text.data,
                      date_created=datetime.now())
        DB.session.add(tweet)
        DB.session.commit()

        return redirect(url_for('timeline'))

    return 'Something went wrong!'


@APP.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        image_filename = PHOTOS.save(form.image.data)
        image_url = PHOTOS.url(image_filename)

        new_user = User(name=form.name.data, username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        image=image_url, join_date=datetime.now())
        DB.session.add(new_user)
        DB.session.commit()

        login_user(new_user)
        return redirect(url_for('profile'))

    return render_template('register.html', form=form)


@APP.route('/follow/<username>')
@login_required
def follow(username):
    user_to_follow = User.query.filter_by(username=username).first()
    current_user.following.append(user_to_follow)
    DB.session.commit()
    return redirect(url_for('profile'))
