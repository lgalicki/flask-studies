"""
Handles database connection for Members API.

Created in 2020/03/01.
"""

import sqlite3 as db
from flask import g

def connect_db():
    """
    Connects to SQLite.
    """
    connection = db.connect('members.db')
    connection.row_factory = db.Row
    return connection


def get_db():
    """
    Returns the connection to SQLite.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
