from flask import Flask, jsonify, request, url_for, redirect

app = Flask(__name__)

# Below is na example of how to configure Flask easily. It's commented because
# I opted for passing this parameter as an argument.
# app.config['DEBUG'] = True

# This is a simple example of how to write a Flask app.
@app.route('/')
def index():
    return """
        <H1>Hello, world! Why don't you try to access the <A HREF='/cool'>/cool</A>
        subpath?</H1><BR>
        <H1>You can also check a JSON being returned by clicking
        <A HREF='/json'>here</A>!</H1>
    """

# This is another one, in a subpath.
@app.route('/cool')
def cool():
    return "<H1>You're now in the /cool subpath!</H1>"

# This is how you can return a JSON object.
@app.route('/json')
def json():
    my_dict = {'key1': 'value1', 'key2': [1, 2, 3]}
    return jsonify(my_dict)

# An example showing how we can limit the accepted request to POST.
@app.route('/post_only', methods=['POST'])
def post_only():
    return "<H1>This can be access only by a POST request</H1>"

# An example showing how we can limit the accepted request to GET.
@app.route('/get_only', methods=['GET'])
def get_only():
    return """
        <H1>This can be access only by a GET request</H1><BR>
        Remember that, by default, Flask will allow only GET if nothing is specified.
        """
# And here and example of how to accept two or more methods.
@app.route('/post_get', methods=['POST', 'GET'])
def post_get():
    return "<H1>This can be access either POST or GET requests</H1>"

# Here we have an example of how we can receive a single parameter through the
# URL. We must access it as /parm/<Your_name_here>. The type of the variable is
# not obligatory, but, if we define it, 404 is returned if we specify a value which
# doesn't fit it. The first decorator, if defined, prevents 404 in case the
# argument is not specified. Its methods and argument name must be exactly the
# same as the decorator right below it.
@app.route('/parm', methods=['GET', 'POST'], defaults={'name': 'Zé Ninguém'})
@app.route('/parm/<string:name>', methods=['GET', 'POST'])
def parm(name):
    return f"<H1>Hello, {name}</H1>"

# This is how we get vales from a query string.
@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return f"<H1>Hi, {name}! How's the weather in {location}?</H1>"

# And the following two routes demonstrate how we get data from a form.
@app.route('/theform')
def theform():
    return """
        <FORM METHOD="POST" ACTION='/process'>
            <INPUT TYPE='TEXT' NAME='name'><BR>
            <INPUT TYPE='TEXT' NAME='location'><BR>
            <INPUT TYPE='SUBMIT' VALUE="Let's go!">
        </FORM>
        """
@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    location = request.form['location']

    return f"<H1>How's the weather in {location}, {name}?</H1>"

# Below we have an example of how we can process incoming JSON.
@app.route('/processjson', methods=['POST'])
def processjson():
    data = request.get_json()
    name = data['name'].upper()
    location = data['location'].upper()
    randomlist = data['randomlist']
    
    return jsonify({
        'nome': name,
        'localizacao': location,
        '2nd_elem_list': randomlist[1].upper()
        })

# Below we see how we can make a single route handle two different methods.
@app.route('/post_get_form', methods=['GET', 'POST'])
def post_get_form():
    if request.method == 'GET':
        return """
            What's your name?
            <FORM METHOD="POST" ACTION="/post_get_form">
                <INPUT TYPE="TEXT" NAME="name" VALUE="John Doe"><BR>
                <INPUT TYPE="SUBMIT" VALUE="Hit it!">
            </FORM>
        """
    else:
        name = request.form['name']
        return f'<H1>Your name is {name}.</H1>'

# There's another way to deal with what has been show right above. We can define
# the same route more than once. Check it out. Notice how the two blocks are
# differentiated by the HTTP methods.
@app.route('/post_get_form2')
def post_get_form2_get():
        return """
            What's your name?
            <FORM METHOD="POST" ACTION="/post_get_form2">
                <INPUT TYPE="TEXT" NAME="name" VALUE="Tonto"><BR>
                <INPUT TYPE="SUBMIT" VALUE="Hit it!">
            </FORM>
        """

@app.route('/post_get_form2', methods=['POST'])
def post_get_form2_post():
        name = request.form['name']
        return f'<H1>Yer name is {name}.</H1>'

# Now let's see how to redirect the user. We use:
# url_for: this returns the URL for a given method. Hear it? Method!
# redirect: pretty self explanatory.
@app.route('/redirection', methods = ['GET', 'POST'])
def redirection():
    if request.method == 'GET':
        return """
            <FORM METHOD="POST" ACTION='/redirection'>
                <INPUT TYPE='TEXT' NAME='name'><BR>
                <INPUT TYPE='TEXT' NAME='location'><BR>
                <INPUT TYPE='SUBMIT' VALUE="Redirect me!">
            </FORM>
            """
    else:
        name = request.form['name']
        location = request.form['location']
        return redirect(url_for('parm', name=name, location=location))


if __name__ == '__main__':
    # debug=True prevents us from restarting the app everytime we make a change to it.
    app.run(debug=True)

