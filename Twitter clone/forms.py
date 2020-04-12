from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Length, InputRequired
from flask_uploads import IMAGES


class RegisterForm(FlaskForm):
    name = StringField('Full name',
                       validators=[InputRequired('Full name is required'),
                                   Length(max=100, message="Name can't be longer than 100 chars")])
    username = StringField('Username',
                           validators=[InputRequired('Username is required'),
                                       Length(max=100,
                                              message="Username can't be longer than 30 chars")])
    password = PasswordField('Password',
                             validators=[InputRequired('Password is required')])
    image = FileField(validators=[FileAllowed(IMAGES, 'Invalid image file')])


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired('Username is required'),
                                       Length(max=100,
                                              message="Username can't be longer than 30 chars")])
    password = PasswordField('Password',
                             validators=[InputRequired('Password is required')])
    remember = BooleanField('Remember me')


class TweetForm(FlaskForm):
    text = TextAreaField('Message', validators=[InputRequired('Type a message')])
