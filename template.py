"""
The templates must be in a folder called 'templates' inside the Flask app folder.

In one of the HTMLs referenced by this program I also have an example of how
Jinja includes static files into a template. I'm talking about template2g.html.
"""
from flask import Flask, render_template, request


APP = Flask(__name__)
APP.config['DEBUG'] = True


# Demonstration of a simple template
@APP.route('/template1')
def template():
    return render_template('template1.html')


# Demonstration of templates with variables. There are also some cool Jinja
# commands inside the HTML templates.
@APP.route('/template2', methods=['GET', 'POST'])
def template2():
    if request.method == 'GET':
        return render_template('template2g.html')

    name = request.form['name']

    if request.form.get('happy'):
        happy = True
    else:
        happy = False

    my_list = ('fish', 'ball', 'cat')
    dict_list = [{'name': 'Júpiter'}, {'name': 'Circó'}]
    return render_template('template2p.html', name=name, happy=happy,
                           my_list=my_list, dict_list=dict_list)

# Demonstration of template inheritance. Check the Jinja commands in the HTML
# templates. There's also a demonstration of the include command here.
@APP.route('/template3')
def template3():
    return render_template('child.html', var='xpto')


if __name__ == '__main__':
    APP.run()
