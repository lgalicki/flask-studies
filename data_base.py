"""
Here we see how to use databases with Flask.

g is some sort of global object, by the way.
"""

import sqlite3 as db
from flask import Flask, g, render_template, request, redirect, url_for

APP = Flask(__name__)
APP.config['DEBUG'] = True


def connect_db():
    connection = db.connect('users.db')
    connection.row_factory = db.Row # This makes things return in a dictionary!
    return connection


def get_db():
    if not hasattr(g, 'db_connection'):
        g.db_connection = connect_db()
    return g.db_connection


# This is executed everytime a route is returned.
@APP.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_connection'):
        g.db_connection.close()


@APP.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'GET':
        db_con = get_db()
        cursor = db_con.cursor()
        sql = 'SELECT id, name, location FROM users;'
        cursor.execute(sql)
        res_query = cursor.fetchall()
    
        return render_template('database.html', items=res_query)            
    
    else:
        name = request.form['name']
        location = request.form['location']

        db_con = get_db()
        sql = 'INSERT INTO users (name, location) VALUES (?, ?);'
        db_con.execute(sql, [name, location])
        db_con.commit()

        return redirect(url_for('index'))


if __name__ == '__main__':
    APP.run()
