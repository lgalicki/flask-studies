from flask_login import UserMixin
from app import DB


followers = DB.Table('follower',
                     DB.Column('follower_id', DB.Integer, DB.ForeignKey('user.id')),
                     DB.Column('followee_id', DB.Integer, DB.ForeignKey('user.id')))


class User(DB.Model, UserMixin):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100))
    username = DB.Column(DB.String(30))
    image = DB.Column(DB.String(100))
    password = DB.Column(DB.String(50))
    join_date = DB.Column(DB.DateTime)

    tweets = DB.relationship('Tweet', backref='user', lazy='dynamic')

    following = DB.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followee_id == id),
                                backref=DB.backref('followers', lazy='dynamic'),
                                lazy='dynamic')

    followed_by = DB.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.followee_id == id),
                                secondaryjoin=(followers.c.follower_id == id),
                                backref=DB.backref('followees', lazy='dynamic'),
                                lazy='dynamic')


class Tweet(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))
    text = DB.Column(DB.String(140))
    date_created = DB.Column(DB.DateTime)
