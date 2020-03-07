from flask import Flask
from flask_mail import Mail, Message
from mail_credentials import MailCredentials as mc

APP = Flask(__name__)

APP.config['DEBUG'] = True
APP.config['TESTING'] = False
APP.config['MAIL_SERVER'] = 'smtp.gmail.com' 
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
#APP.config['MAIL_DEBUG'] = True # default inherits from 'DEBUG'
APP.config['MAIL_USERNAME'] = mc.user
APP.config['MAIL_PASSWORD'] = mc.password
APP.config['MAIL_DEFAULT_SENDER'] = ('Pedro de Lara', mc.user)
APP.config['MAIL_MAX_EMAILS'] = None
#APP.config['MAIL_SUPPRESS_SEND'] = False # default inherits from 'TESTING'. Will suppress mail sending
APP.config['MAIL_ASCII_ATTACHMENTS'] = False # if false will use Unicode

mail = Mail(APP)

# It could also be started like this
# mail = Mail()
# mail.init_app(APP)


@APP.route('/')
def index():
    msg = Message('Subject here', recipients=['pigaw43568@emailnube.com'])
    msg.html = """
    <H1>Hello there!</H1><BR>
    This is where you'll put the e-mail body. You could also specify the
    body in the <I>msg.body</I> attribute, but then you wouldn't be able to
    use <B>HTML</B>.
    """
    
    # This is another way of sending to more than one recipient
    # msg.add_recipient('email@address.com')
    
    with APP.open_resource('flores.jpg') as flores:
        msg.attach('Para você.jpg', 'image/jpg', flores.read())
    
    mail.send(msg)

    return 'Message has been sent'


# This is an example of how you should send bulk mails. They'll be all sent in a single connection.
# If you use the method above you'll reveal all recipient e-mails to everybody,
# so stick to this bulk method!
@APP.route('/bulk')
def bulk():
    users = ['pigaw43568@emailnube.com', 'gacoliw183@mailernam.com']
    
    with mail.connect() as conn:
        for user in users:
            msg = Message('Bulk mail example', recipients=[user])
            msg.html = """
            <H1>Hello there!</H1><BR>
            This is where you'll put the e-mail body. You could also specify the
            body in the <I>msg.body</I> attribute, but then you wouldn't be able to
            use <B>HTML</B>.
            """
            conn.send(msg)

    return ''

if __name__ == '__main__':
    APP.run()
