from flask import Flask, request, session, url_for, redirect

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'MyNotSoRandonKey'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return """
            Your name:
            <FORM METHOD="POST" ACTION="/">
                <INPUT TYPE="TEXT" NAME="name">
                <INPUT TYPE="SUBMIT" VALUE="Confirm">
            </FORM>
        """
    else:
        # Here we'll set the name informed as a session variable. All routes
        # will be able to access it even though it won't be directly passed
        # in the requests.
        session['name'] = request.form['name']
        return redirect(url_for('decision'))


@app.route('/decision')
def decision():
    # Here we check if we've got the session variable and use it, if it exists.
    if 'name' in session:
        name = session['name']
    else:
        name = 'No name defined.'

    return f"""
        Hello, {name}.
        <BR>
        <FORM METHOD="GET" ACTION="/">
            <INPUT TYPE="SUBMIT" VALUE="Redefine session var">
        </FORM>
        
        <FORM METHOD="GET" ACTION="/decision">
            <INPUT TYPE="SUBMIT" VALUE="Show session var">
        </FORM>
        
        <FORM METHOD="GET" ACTION="/delete_session_var">
            <INPUT TYPE="SUBMIT" VALUE="Delete session var">
        </FORM>            
    """

@app.route('/delete_session_var')
def delete_session_var():
    # Here we delete the session variable.
    session.pop('name', None)
    return redirect(url_for('decision'))


if __name__ == "__main__":
    app.run()
