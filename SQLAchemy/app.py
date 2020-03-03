from flask import Flask
from flask_sqlalchemy import SQLAlchemy


APP = Flask(__name__)
APP.config.from_pyfile('config.py')

db = SQLAlchemy(APP)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    email = db.Column(db.String(50))
    join_date = db.Column(db.DateTime)
    
    orders = db.relationship('Order', backref='member', lazy='dynamic')
    courses = db.relationship('Course', secondary='user_courses',
                              backref='member', lazy='dynamic')

    def __repr__(self):
        return f'<Member {self.username}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))

    members = db.relationship('Member', secondary='user_courses',
                              backref='course', lazy='dynamic')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

db.Table('user_courses',
         db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
         db.Column('course_id', db.Integer, db.ForeignKey('course.id')))


if __name__ == '__main__':
    APP.run()
