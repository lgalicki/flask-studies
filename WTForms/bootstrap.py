from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, AnyOf
from flask_bootstrap import Bootstrap

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'MySeCrEt!'
bootstrap = Bootstrap()

class LoginForm(FlaskForm): # IMPORTANT: there can be only one FlaskForm per form. 
    username = StringField('Yer username:',
                           validators=[InputRequired(),
                                       Length(min=3, max=10, message='Wrong length')])
    password = PasswordField('Yer Pass:',
                             validators=[InputRequired(),
                                         Length(min=3, max=10, message='Wrong length'),
                                         AnyOf(values=['secret', 'password'], message="Wrong pass.")])



@APP.route('/bootstrap', methods=['GET', 'POST'])
def bootstrap():

    form = LoginForm()

    if form.validate_on_submit():
        return '<H1>Form submitted successfully!</H1>'

    return render_template('bootstrap.html', form=form)


if __name__ == '__main__':
    APP.run(debug=True)
