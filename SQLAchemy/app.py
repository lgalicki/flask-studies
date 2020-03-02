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

    def __repr__(self):
        return f'<Member {self.username}>'

if __name__ == '__main__':
    APP.run()
