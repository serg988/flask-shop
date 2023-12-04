# python3 -m venv venv
# source venv/bin/activate

from flask import Flask, render_template, flash, session, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os

app = Flask(__name__)
bootstrap = Bootstrap5(app)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="root",
    password="password!",
    hostname="localhost",
    databasename="shop",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(30))
    password = db.Column(db.String(200))

    # def __repr__(self):
    #     return [self.name, self.text]


class Product(db.Model):
    __tablename__ = "product"
    product_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    product_name = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    image = db.Column(db.String(500))

    # def __repr__(self):
    #     return [self.name, self.text]


app.config['SECRET_KEY'] = os.urandom(24)


def is_authenticated():
    username = session.get('username')
    return username and len(username.strip()) > 0


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            return redirect('login')
        return f(*args, **kwargs)
    return wrapper


@app.route('/')
@login_required
def index():
    products = Product.query.all()
    cats = set([cat.category for cat in products])
    return render_template('products.html', products=products, cats=cats)


@app.route('/products/<cat>')
@login_required
def products(cat):
    products = Product.query.all()
    cats = set([cat.category for cat in products])
    filtered_products = products = Product.query.filter(
        Product.category == cat)
    return render_template('products.html', products=filtered_products, cats=cats)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if not request.form["username"] or not request.form["password"]:
            flash("Поля не должны быть пустыми.", 'danger')
            return render_template('login.html')
        else:
            entered_username = request.form["username"]
            password = request.form["password"]
            user_stored = User.query.filter_by(
                username=entered_username).first()
            if not user_stored:
                flash("Неправильное имя пользователя или пароль", 'danger')
                return redirect('/login')
            if not check_password_hash(user_stored.password, password):
                flash('Неправильное имя пользователя или пароль', 'danger')
                return render_template('/login.html')
            session['username'] = entered_username
            session['login'] = True
            if entered_username.lower() == 'admin':
                session['is_admin'] = True
            return redirect('/')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_details = request.form
        if user_details['password'] != user_details['confirmPassword']:
            flash("Пароли не совпадают. Попробуйте еще.", 'danger')
            return render_template('register.html')
        else:
            user = User(
                username=request.form["username"],
                first_name=request.form["firstname"],
                last_name=request.form["lastname"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"]),
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please login.", 'success')
            return redirect('/login')
    return render_template('register.html')


@app.route('/product-form', methods=['GET', 'POST'])
def product_form():
    if request.method == 'POST' and request.form.get('del'):
        Product.query.filter(Product.product_id ==
                             request.form['del'][6:]).delete()
        db.session.commit()
        return redirect('/')
    elif request.method == 'POST':
        product = Product(
            category=request.form["category"],
            product_name=request.form["product_name"],
            quantity=request.form["quantity"],
            price=request.form["price"],
            image=request.form["image"],
        )
        db.session.add(product)
        db.session.commit()
        flash("Товар добавлен!", 'success')
        return redirect('/product-form')
    return render_template('product-form.html')


@app.route('/about')
@login_required
def about():
    return render_template('/about.html')


@app.route('/logout/')
def logout():
    session.clear()
    flash("Вы вышли из аккаунта", 'info')
    return redirect('/login')


if (__name__ == '__main__'):
    app.run(debug=True)

# CREATE TABLE user(user_id int auto_increment PRIMARY KEY, username varchar(20), first_name varchar(20), last_name varchar(20), email varchar(30), p
# assword varchar(200));

# CREATE TABLE product(product_id int auto_increment PRIMARY KEY, category varchar(50), product_name varchar(30), quantity int, price int, image varc
# har(500));

# ALTER TABLE product ADD COLUMN image varchar(150) AFTER text;
