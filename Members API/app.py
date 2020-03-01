"""
Members API as shown in the Udemu Flask course.

Created in 2020/03/01.
"""
from functools import wraps
from flask import Flask, g, request, jsonify
from flask_api import status
from database import get_db


APP = Flask(__name__)

USERNAME = 'admin'
PASSWORD = 'admin'


def autheticate(func):
    """
    Validates username and password of whom is trying to access the API.
    """
    @wraps(func)
    def wrapper_authenticate(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == USERNAME and auth.password == PASSWORD:
            return func(*args, **kwargs)

        return jsonify({'message': 'Not authorized'}), \
            status.HTTP_403_FORBIDDEN

    return wrapper_authenticate


@APP.teardown_appcontext
def close_db(error):
    """
    Executed everytime a route reachs its end.
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@APP.route('/member', methods=['GET'])
@autheticate
def get_members():
    """
    Returns list of all memembers.
    """
    sql = """
        SELECT id, name, email, level
        FROM members;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    members_query = cursor.fetchall()

    members_list = list()
    for member in members_query:
        member_dict = dict()
        member_dict['id'] = member['id']
        member_dict['name'] = member['name']
        member_dict['email'] = member['email']
        member_dict['level'] = member['level']

        members_list.append(member_dict)

    return jsonify({'members': members_list})


@APP.route('/member/<int:member_id>', methods=['GET'])
@autheticate
def get_member(member_id):
    """
    Returns details of a single member.
    """
    sql = """
        SELECT id, name, email, level
        FROM members
        WHERE id = ?;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql, [member_id])
    member_query = cursor.fetchone()

    if member_query is None:
        return jsonify({'message': 'Not found'}), status.HTTP_404_NOT_FOUND

    return jsonify({'member': {'id': member_query['id'],
                               'name': member_query['name'],
                               'email': member_query['email'],
                               'level': member_query['level']}})



@APP.route('/member', methods=['POST'])
@autheticate
def add_member():
    """
    Inserts a new member.
    """
    new_member_data = request.get_json()
    name = new_member_data.get('name')
    email = new_member_data.get('email')
    level = new_member_data.get('level')

    sql = """
        INSERT INTO members
        (name, email, level)
        VALUES (?, ?, ?);
    """
    db = get_db()
    db.execute(sql, [name, email, level])
    db.commit()

    sql = """
        SELECT id, name, email, level
        FROM members
        WHERE id = last_insert_rowid();
    """
    cursor = db.cursor()
    cursor.execute(sql)
    inserted_query = cursor.fetchone()

    return jsonify({'member': {'id': inserted_query['id'],
                               'name': inserted_query['name'],
                               'email': inserted_query['email'],
                               'level': inserted_query['level']}})


@APP.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@autheticate
def edit_member(member_id):
    """
    Updates info of a single member.
    """
    upd_member_data = request.get_json()
    name = upd_member_data.get('name')
    email = upd_member_data.get('email')
    level = upd_member_data.get('level')

    sql = """
        UPDATE members
        SET name = ?, email = ?, level = ?
        WHERE id = ?;
    """
    db = get_db()
    db.execute(sql, [name, email, level, member_id])
    db.commit()

    sql = """
        SELECT id, name, email, level
        FROM members
        WHERE id = ?;
    """
    cursor = db.cursor()
    cursor.execute(sql, [member_id])
    updated_query = cursor.fetchone()

    return jsonify({'member': {'id': updated_query['id'],
                               'name': updated_query['name'],
                               'email': updated_query['email'],
                               'level': updated_query['level']}})


@APP.route('/member/<int:member_id>', methods=['DELETE'])
@autheticate
def delete_member(member_id):
    """
    Deletes a single member.
    """
    sql = """
        DELETE FROM members where id = ?;
    """
    db = get_db()
    db.execute(sql, [member_id])
    db.commit()

    return jsonify({'message': 'Member deleted.'})


if __name__ == '__main__':
    APP.run(debug=True)
