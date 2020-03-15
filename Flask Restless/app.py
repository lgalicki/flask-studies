from flask import Flask
from flask_restless import APIManager
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(APP)
MANAGER = APIManager(APP, flask_sqlalchemy_db=DB)


class User(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(20), unique=True)
    items = DB.relationship('Item', backref='user', lazy='dynamic')


class Item(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(20), unique=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('user.id'))


MANAGER.create_api(User, methods=['GET', 'POST'])
MANAGER.create_api(Item, methods=['GET', 'POST', 'DELETE', 'PUT'],
                   allow_delete_many=True, allow_patch_many=True)


if __name__ == '__main__':
    APP.run(debug=True)
