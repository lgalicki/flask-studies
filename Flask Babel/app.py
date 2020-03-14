from flask import Flask, render_template, request
from flask_babel import Babel, get_locale, format_date, format_datetime, gettext
from datetime import date, datetime

APP = Flask(__name__)
BABEL = Babel(APP)


@BABEL.localeselector
def localeselector():
    # Detects the best language based on headers sent by the browser
    return request.accept_languages.best_match(['es_ES', 'pt_BR', 'en_US', 'pt'])


@APP.route('/')
def index():
    d = date(2001, 9, 11)
    dt = datetime(2010, 5, 13, 15, 16)

    local_date = format_date(d)
    local_datetime= format_datetime(dt, 'short')
    
    dog = gettext('Dog')
    cat = gettext('Cat')

    return render_template('index.html', locale=get_locale(), local_date=local_date,
                           local_datetime=local_datetime, dog=dog, cat=cat)


if __name__ == '__main__':
    APP.run(debug=True)
