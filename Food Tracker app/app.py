from datetime import datetime
from flask import Flask, render_template, g, request
from database import get_db

APP = Flask(__name__)


@APP.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@APP.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date'] # Assuming it's coming in yyyy-mm-dd format.
        dt = datetime.strptime(date, '%Y-%m-%d') # Transfoming in a datetime object.
        db_date = datetime.strftime(dt, '%Y%m%d') # Making a string out of the datetime object.

        sql = """
            INSERT INTO log_date (entry_date) VALUES (?);
        """
        db.execute(sql, [db_date])
        db.commit()

    cursor = db.cursor()
    sql = """
        SELECT
        	lg.entry_date,
        	SUM(f.proteins) AS tot_proteins,
        	SUM(f.carbs) AS tot_carbs,
        	SUM(f.fats) AS tot_fats,
        	SUM(f.calories) AS tot_calories
        FROM log_date lg
        LEFT JOIN food_date fd ON fd.log_date_id = lg.id
        LEFT JOIN food f ON f.id = fd.food_id
        GROUP BY lg.entry_date
        ORDER BY lg.entry_date DESC;
    """
    cursor.execute(sql)
    res_query = cursor.fetchall()

    dates = list()
    for item in res_query:
        d = datetime.strptime(str(item['entry_date']), '%Y%m%d')
        date = {'pretty_date': datetime.strftime(d, '%B %d, %Y'),
                'date': item['entry_date'], 'tot_proteins': item['tot_proteins'],
                'tot_carbs': item['tot_carbs'], 'tot_fats': item['tot_fats'],
                'tot_calories': item['tot_calories']}
        dates.append(date)

    return render_template('home.html', results=dates)


@APP.route('/view/<date>', methods=['GET', 'POST']) # date in format yyyymmdd
def view(date):
    db = get_db()

    # Selecting date for table title and its id in case of food_date insertion
    cursor = db.cursor()
    sql = """
        SELECT id, entry_date FROM log_date
        WHERE entry_date = ?;
    """
    cursor.execute(sql, [date])
    res_query = cursor.fetchone()
    date_id = res_query['id']
    date_date = res_query['entry_date']

    # A POST. This means we're adding a food for the date.
    if request.method == 'POST':
        sql = """
            INSERT INTO food_date (food_id, log_date_id)
            VALUES (?, ?);
        """
        db.execute(sql, [request.form['food-select'], date_id])
        db.commit()

    # Here we format the date to display it pretty.
    d = datetime.strptime(str(date_date), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    # Selecting available foods for the combo box
    sql = """
        SELECT id, name FROM food;
    """
    cursor.execute(sql)
    food_query = cursor.fetchall()

    # Here we select the foods added to the date.
    sql = """
        SELECT f.name, f.proteins, f.carbs, f.fats, f.calories
        FROM food_date fd
        JOIN food f ON f.id = fd.food_id
        JOIN log_date ld ON ld.id = fd.log_date_id
        WHERE fd.log_date_id = ?;
    """
    cursor.execute(sql, [date_id])
    foods_in_date = cursor.fetchall()

    # Calculating the totals of the day.
    t_proteins = int()
    t_carbs = int()
    t_fats = int()
    t_calories = int()

    for food in foods_in_date:
        t_proteins += food['proteins']
        t_carbs += food['carbs']
        t_fats += food['fats']
        t_calories += food['calories']

    totals = {'proteins': t_proteins, 'carbs': t_carbs, 'fats': t_fats,
              'calories': t_calories}

    # And finally we render the template
    return render_template('day.html', pretty_date=pretty_date,
                           food_list=food_query, foods_in_date=foods_in_date,
                           totals=totals, num_date=date_date)


@APP.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        carbs = int(request.form['carbs'])
        proteins = int(request.form['proteins'])
        fats = int(request.form['fats'])

        calories = carbs * 4 + proteins * 4 + fats * 9

        sql = """
            INSERT INTO food
            (name, proteins, carbs, fats, calories)
            VALUES (?, ?, ?, ?, ?);
        """
        db.execute(sql, [name, proteins, carbs, fats, calories])
        db.commit()

    cursor = db.cursor()
    sql = """
        SELECT name, proteins, carbs, fats, calories
        FROM food;
    """
    cursor.execute(sql)
    res_query = cursor.fetchall()

    return render_template('add_food.html', results=res_query)


if __name__ == '__main__':
    APP.run(debug=True)
