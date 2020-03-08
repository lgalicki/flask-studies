from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from mysql_credentials import MysqlCredentials as dbc

APP = Flask(__name__)
# APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
APP.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{dbc.user}:{dbc.password}@localhost/flask_migrate'

DB = SQLAlchemy(APP)

MIGRATE = Migrate(APP, DB)

MANAGER = Manager(APP)
MANAGER.add_command('DB', MigrateCommand)

class Member(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(50))
    subscribed = DB.Column(DB.Boolean)

class Orders(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    total = DB.Column(DB.Integer)

if __name__ == '__main__':
    MANAGER.run()
    APP.run(debug=True)
