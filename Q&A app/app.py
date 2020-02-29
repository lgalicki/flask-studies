import os
from flask import Flask, render_template, g, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

APP = Flask(__name__)
APP.config['SECRET_KEY'] = os.urandom(24)


def get_user_info():
    if 'user' in session:
        user_info = dict()
        user_info['user'] = session['user']
        user_info['id'] = session['user_id']
        user_info['is_expert'] = 'is_expert' in session
        user_info['is_admin'] = 'is_admin' in session
        return user_info

    return None


@APP.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@APP.route('/')
def index():
    user = get_user_info()

    sql = """
        SELECT
            q.id AS q_id,
            q.question_text,
            asker.name AS asker_name,
            expert.name AS expert_name
        FROM questions q
        JOIN users asker ON asker.id = q.asked_by_id
        JOIN users expert ON expert.id = q.expert_id
        WHERE q.answer_text IS NOT NULL;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    questions_query = cursor.fetchall()

    return render_template('home.html', user=user, questions=questions_query)


@APP.route('/register', methods=['GET', 'POST'])
def register():
    user = get_user_info()
    message = str()

    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name.isspace() or not name or password.isspace() or not password:
            message = 'ERROR: name and password must be informed'

        else:
            db = get_db()
            cursor = db.cursor()
            sql = """
                SELECT name FROM users
                WHERE name = ?;
            """
            cursor.execute(sql, [name])
            name_query = cursor.fetchone()

            name_exists = bool()
            if name_query is not None:
                name_exists = True
                message = f'ERROR: user {name} already exists'

            if not name_exists:
                message = f'User {name} created with success'
                hashed_password = generate_password_hash(password, method='sha256')

                sql = """
                    INSERT INTO users
                    (name, password, expert, admin)
                    VALUES (?, ?, ?, ?)
                """
                db.execute(sql, [name, hashed_password, False, False])
                db.commit()

    return render_template('register.html', message=message, user=user)


@APP.route('/login', methods=['GET', 'POST'])
def login():
    user = get_user_info()
    message = str()

    if request.method == 'POST':
        in_name = request.form['name']
        in_password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        sql = """
            SELECT id, password, admin, expert FROM users
            WHERE name = ?;
        """
        cursor.execute(sql, [in_name])
        user_query = cursor.fetchone()

        if user_query is None:
            message = 'Invalid credentials'
        else:
            db_password = user_query['password']
            is_admin = user_query['admin']
            is_expert = user_query['expert']
            user_id = user_query['id']

            if check_password_hash(db_password, in_password):
                session['user'] = in_name
                session['user_id'] = user_id

                if is_admin:
                    session['is_admin'] = True

                if is_expert:
                    session['is_expert'] = True

                return redirect(url_for('index'))

            message = 'Invalid credentials'

    return render_template('login.html', message=message, user=user)


@APP.route('/question/<question_id>')
def question(question_id):
    user = get_user_info()

    sql = """
        SELECT
            q.answer_text,
            q.question_text,
            asker.name AS asker_name,
            expert.name AS expert_name
        FROM questions q
        JOIN users asker ON asker.id = q.asked_by_id
        JOIN users expert ON expert.id = q.expert_id
        WHERE q.id = ?;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql, [question_id])
    question_query = cursor.fetchone()

    return render_template('question.html', user=user, question=question_query)


@APP.route('/answer/<question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_user_info()

    if not user:
        return redirect(url_for('login'))

    if not user['is_expert']:
        return redirect(url_for('index'))

    message = str()

    if request.method == 'POST':
        answer = request.form['answer']
        if not answer or answer.isspace():
            message = 'ERROR: blank response is not allowed'
        else:
            db = get_db()
            sql = """
                UPDATE questions SET answer_text = ?
                WHERE id = ?;
            """
            db.execute(sql, [answer, question_id])
            db.commit()
            return redirect(url_for('unanswered'))

    db = get_db()
    cursor = db.cursor()
    sql = """
        SELECT id, question_text FROM questions
        WHERE id = ?;
    """
    cursor.execute(sql, [question_id])
    question_query = cursor.fetchone()
    return render_template('answer.html', user=user, question=question_query,
                           message=message)


@APP.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_user_info()
    
    if not user:
        return redirect(url_for('login'))

    if user['is_admin'] or user['is_expert']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        sql = """
            INSERT into questions
            (question_text, asked_by_id, expert_id)
            VALUES (?, ?, ?);
        """
        db_i = get_db()
        db_i.execute(sql, [request.form['question'], user['id'],
                           request.form["expert"]])
        db_i.commit()

        return redirect(url_for('index'))

    # Populating the experts combo box.
    sql = """
        SELECT id, name FROM users WHERE expert = True;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    exp_query = cursor.fetchall()

    return render_template('ask.html', user=user, experts=exp_query)


@APP.route('/unanswered')
def unanswered():
    user = get_user_info()
    
    if not user:
        return redirect(url_for('login'))

    if not user['is_expert']:
        return redirect(url_for('index'))
    
    # Fetching the unanswered question for the logged in expert.
    sql = """
            SELECT q.id, q.question_text, u.name
            FROM questions q
            JOIN users u ON u.id = q.asked_by_id
            WHERE q.answer_text IS NULL
              AND q.expert_id = ?;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql, [user['id']])
    questions_query = cursor.fetchall()

    return render_template('unanswered.html', user=user,
                           questions=questions_query)


@APP.route('/users')
def users():
    user = get_user_info()

    if not user:
        return redirect(url_for('login'))

    if not user['is_admin']:
        return redirect(url_for('index'))

    sql = """
        SELECT id, name, expert FROM users;
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(sql)
    users_query = cursor.fetchall()

    return render_template('users.html', user=user, users=users_query)


@APP.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('is_admin', None)
    session.pop('is_expert', None)
    return redirect(url_for('index'))


@APP.route('/promote/<p_user>')
def promote(p_user):
    user = get_user_info()

    if not user:
        return redirect(url_for('login'))

    if not user['is_admin']:
        return redirect(url_for('index'))

    sql = """
        UPDATE users SET expert = NOT(expert) WHERE id = ?;
    """
    db = get_db()
    db.execute(sql, p_user)
    db.commit()
    return redirect(url_for('users'))


if __name__ == '__main__':
    APP.run(debug=True)
