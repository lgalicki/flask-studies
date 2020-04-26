import os, random, string
from flask import Flask, render_template, redirect, url_for, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField
from flask_wtf.file import FileField, FileAllowed

APP = Flask(__name__)

PHOTOS = UploadSet('photos', IMAGES)

APP.config['UPLOADED_PHOTOS_DEST'] = 'images'
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trendy.db'
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['DEBUG'] = True
APP.config['SECRET_KEY'] = os.urandom(300)

configure_uploads(APP, PHOTOS)

DB = SQLAlchemy(APP)
MIGRATE = Migrate(APP, DB)

MANAGER = Manager(APP)
MANAGER.add_command('DB', MigrateCommand)


class Product(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(50), unique=True)
    price = DB.Column(DB.Integer) # in cents
    stock = DB.Column(DB.Integer)
    description = DB.Column(DB.String(500))
    image = DB.Column(DB.String(100))
    orders = DB.relationship('Order_Item', backref='product', lazy=True)


class Order(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    reference = DB.Column(DB.String(5))
    first_name = DB.Column(DB.String(20))
    last_name = DB.Column(DB.String(20))
    phone_number = DB.Column(DB.Integer)
    email = DB.Column(DB.String(50))
    address = DB.Column(DB.String(100))
    city = DB.Column(DB.String(100))
    state = DB.Column(DB.String(20))
    country = DB.Column(DB.String(20))
    status = DB.Column(DB.String(10))
    payment_type = DB.Column(DB.String(10))
    items = DB.relationship('Order_Item', backref='order', lazy=True)

    def order_total(self):
        return DB.session.query(DB.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + 1000


class Order_Item(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    order_id = DB.Column(DB.Integer, DB.ForeignKey('order.id'))
    product_id = DB.Column(DB.Integer, DB.ForeignKey('product.id'))
    quantity = DB.Column(DB.Integer)


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted')])


class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('id')


class Checkout(FlaskForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=[('CA', 'California'),
                                          ('WA', 'Washington'), ('NV', 'Nevada')])
    country = SelectField('Coutry', choices=[('US', 'United States'), ('UK', 'United Kingdom'),
                                             ('FRA', 'France')])
    payment_type = SelectField('Payment Type', choices=[('CK', 'Check'),
                                                        ('WT', 'Wire Transfer')])


def handle_cart():
    products = list()
    grand_total = int()    

    if 'cart' in session:
        for pos, item in enumerate(session.get('cart')):
            product = Product.query.filter_by(id=item.get('id')).first()
            quantity = int(item.get('quantity'))
            total = quantity * product.price
            grand_total += total
    
            products.append({'name': product.name, 'price': product.price,
                             'image': product.image, 'quantity': quantity,
                             'total': total, 'id': product.id, 'pos': pos})

    grand_total_plus_shipping = grand_total + 1000 #because it's in cents

    return products, grand_total, grand_total_plus_shipping


@APP.route('/')
def index():
    products = Product.query.all()

    return render_template('index.html', products=products)


@APP.route('/product/<id>')
def product(id):
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    if product:
        return render_template('view-product.html', product=product, form=form)

    abort(404)


@APP.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = list()

    session['cart'].append({'id': id, 'quantity': 1})
    session.modified = True # because Flask can't detect changes in mutable variables

    return redirect(url_for('index'))


@APP.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = list()

    form = AddToCart()

    if form.validate_on_submit():
        session['cart'].append({'id': form.id.data, 'quantity': form.quantity.data})
        session.modified = True # because Flask can't detect changes in mutable variables

    return redirect(url_for('index'))


@APP.route('/cart')
def cart():
    products, grand_total, grand_total_plus_shipping = handle_cart()

    return render_template('cart.html', products=products, grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping)


@APP.route('/delete-from-cart/<pos>')
def delete_from_cart(pos):
    del session['cart'][int(pos)]
    session.modified = True # because flask can't notice changes in mutables variables

    return redirect(url_for('cart'))


@APP.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session:
        return redirect(url_for('index'))

    form = Checkout()

    products, grand_total, grand_total_plus_shipping = handle_cart()

    if form.validate_on_submit():
        order = Order()
        form.populate_obj(order)
        order.reference = ''.join([random.choice(string.ascii_uppercase +
                                                 string.digits) for _ in range(5)])
        order.status = 'Pending'

        for product in products:
            order_item = Order_Item(quantity=product.get('quantity'),
                                    product_id=product.get('id'))
            order.items.append(order_item)

            product = Product.query.filter_by(id=product['id']).update({'stock': Product.stock - product['quantity']})

        DB.session.add(order)
        DB.session.commit()
        
        del session['cart']
        session.modified = True

        return redirect(url_for('index'))

    return render_template('checkout.html', form=form, products=products,
                           grand_total=grand_total,
                           grand_total_plus_shipping=grand_total_plus_shipping)


@APP.route('/admin')
def admin():
    orders = Order.query.all()
    products = Product.query.all()
    qt_prods_in_stock = Product.query.filter(Product.stock > 0).count()
    return render_template('admin/index.html', admin=True, products=products,
                           qt_prods_in_stock=qt_prods_in_stock, orders=orders)


@APP.route('/admin/add', methods=['GET', 'POST'])
def add():
    form = AddProduct()

    if form.validate_on_submit():
        image_url = PHOTOS.url(PHOTOS.save(form.image.data))
        new_product = Product(name=form.name.data, price=form.price.data,
                              stock=form.stock.data, description=form.description.data,
                              image=image_url)

        DB.session.add(new_product)
        DB.session.commit()

        return redirect(url_for('admin'))

    return render_template('admin/add-product.html', admin=True, form=form)


@APP.route('/admin/order/<id>')
def order(id):
    order = Order.query.filter_by(id=int(id)).first()
    return render_template('admin/view-order.html', admin=True, order=order)


if __name__ == '__main__':
    MANAGER.run()
