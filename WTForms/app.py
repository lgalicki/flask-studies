from collections import namedtuple
from flask import Flask, render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, IntegerField, BooleanField, \
Form, FormField, FieldList, DateField
from wtforms.validators import InputRequired, Length, AnyOf, Email, ValidationError

APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'MySeCrEt!'
APP.config['WTF_CSRF_SECRET_KEY'] = 'aNOtherKey!' # If you don't wanna save the default
APP.config['WTF_CSRF_TIME_LIMIT'] = 3600 # This is the default value in seconds
# CSRF errors can be tested with form.csrf_token.errors, like a field. This test
# can be here or in the HTML template.
APP.config['RECAPTCHA_PUBLIC_KEY'] = '6LevhN8UAAAAAPP1lHFHLLNDcEaBq3HvqrG5SXZB'
APP.config['RECAPTCHA_PRIVATE_KEY'] = '6LevhN8UAAAAAJnSshZr-VcT4tr9tSNMzYvCmEUg'
# APP.config['TESTING'] = True Use this is if you don't wanna keep filling the recaptcha form while developing.

# Notice this is not a FlaskForm because we can have only one FlaskForm
class PhoneForm(Form):
    country = IntegerField('country code')
    area = IntegerField('area')
    number = StringField('phone number')

# This class is only for demonstration of the populate_obj method. Its methods
# names are matched up to the form fields' names.
class MyObj():
    def __init__(self):
        self.username = str()
        self.age = int()

# Notice this is not a FlaskForm because we can have only one FlaskForm
class DogForm(Form):
    dog_name = StringField('name')
    age = IntegerField('age')


class LoginForm(FlaskForm): # IMPORTANT: there can be only one FlaskForm per form. 
    username = StringField('Yer username:',
                           validators=[InputRequired(),
                                       Length(min=3, max=10, message='Wrong length')])
    password = PasswordField('Yer Pass:',
                             validators=[InputRequired(),
                                         Length(min=3, max=10, message='Wrong length'),
                                         AnyOf(values=['secret', 'password'], message="Wrong pass.")])
    age = IntegerField('age', default=69)
    fav_day = DateField('favourite day', format='%Y/%m/%d') # could use the HMTL5 too.
    checkbox = BooleanField('Wanna click here?')
    email = StringField('mail', validators=[Email()])
    home_phone = FormField(PhoneForm)
    work_phone = FormField(PhoneForm)
    dogs = FieldList(FormField(DogForm))
    unused = StringField() # This is used to demonstrate how to hide unwanted fields.
    recaptcha = RecaptchaField()
    
    # Below we have an example of inline validator
    def validate_age(form, field):
        if field.data == 69:
            raise ValidationError("Your age is too pornographic.")

    
# This is just to demonstrate form inheritance.
class NameForm(LoginForm):
    first_name = StringField()
    last_name = StringField()


# This is for demonstration of form pre-populating. Forms will usually be pre-
# populated by a DB object. What matters is that the attributes of the object
# must have the same names as the ones the form fields have.
class User():
    def __init__(self, username, email):
        self.username = username
        self.email = email


@APP.route('/', methods=['GET', 'POST'])
def index():
    xpto = User('Pedrinho', 'pedrinho@pedrinha.com')

    # This is for demonstration purposes. FieldList is usually used with records
    # read in a database.
    pack = namedtuple('Pack', ['dog_name', 'age'])
    dog1 = pack('Júpiter', 6)
    dog2 = pack('Circó', 10)
    dog3 = pack('Lelê', 38)
    dogs = {'dogs': [dog1, dog2, dog3]}

    form = NameForm(obj=xpto, data=dogs)
    
    # Check your terminal!
    my_obj = MyObj()
    #form.populate_obj(my_obj) -> commented because the form is too comples and I'm lazy to define a object that looks like exaclty like it.
    print(my_obj.username)
    print(my_obj.age)
    
    # Suppose in a given condition you don't what to show a field. Use this.
    del form.unused

    if form.validate_on_submit():
        pack_data = str()
        for dog in form.dogs:
            pack_data += f'<br>{dog.dog_name.data}, {dog.age.data}'
        
        return f'User: {form.username.data}, pass: {form.password.data},' \
            f' age: {form.age.data}, checkbox: {form.checkbox.data}, ' \
            f'email: {form.email.data}, first name: {form.first_name.data}, ' \
            f'last name: {form.last_name.data},' \
            f'home phone: {form.home_phone.country.data} {form.home_phone.area.data} {form.home_phone.number.data}' \
            f'work phone: {form.work_phone.country.data} {form.work_phone.area.data} {form.work_phone.number.data}' \
            f'{pack_data}'

    return render_template('index.html', form=form)


@APP.route('/dynamic', methods=['GET', 'POST'])
def dynamic():
    class DynamicForm(FlaskForm):
        pass
    
    names = ['first name', 'middle name', 'last name', 'nickname']
    for name in names:
        setattr(DynamicForm, name, StringField(name))

    form = DynamicForm()

    if form.validate_on_submit():
        data = str()
        for field in form:
            data += field.data + '<br>l'

        return data
    return render_template('dynamic.html', form=form, names=names)


if __name__ == '__main__':
    APP.run(debug=True)
