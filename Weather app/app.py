import requests
import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
from flask_migrate import Migrate
from api_credentials import ApiCredentials as ac


APP = Flask(__name__)
APP.config['SECRET_KEY'] = os.urandom(300)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cities.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['DEBUG'] = True
DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)


class City(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.Integer, unique=True)
    

class AddCity(FlaskForm):
    city_name = StringField('City', validators=[InputRequired()])


@APP.route('/', methods=['GET', 'POST'])
def index():
    form = AddCity()
    
    if form.validate_on_submit():
        new_city = City(name=form.city_name.data)
        DB.session.add(new_city)
        DB.session.commit()

    cities = City.query.order_by(City.name).all()
    
    weather_info = list()
    for city in cities:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city.name}&APPID={ac.key}&units=metric'
        city_info = requests.get(url).json()
        
        weather = {'name': city_info.get('name'),
                   'temperature': city_info.get('main').get('temp'),
                   'description': city_info.get('weather')[0].get('main') + 
                   ' - ' + city_info.get('weather')[0].get('description'),
                   'icon': city_info.get('weather')[0].get('icon')}

        weather_info.append(weather)

    return render_template('weather.html', form=form, weather_info=weather_info)


if __name__ == '__main__':
    APP.run()
