from flask import Flask, render_template
from flask_bootstrap import Bootstrap

APP = Flask(__name__)
BOOTSTRAP = Bootstrap(APP)


@APP.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    APP.run(debug=True)
