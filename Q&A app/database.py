import sqlite3 as db
from flask import g

def connect_db():
    connection = db.connect('q&a.db')
    connection.row_factory = db.Row
    return connection


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
