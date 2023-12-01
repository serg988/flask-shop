# python3 -m venv venv
# source venv/bin/activate

from flask import Flask, render_template, flash, session, request, redirect
from flask_bootstrap import Bootstrap5
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# DB Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'shop'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24)


@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM product")
    if result_value > 0:
        products = cursor.fetchall()
        cursor.close()
        return render_template('products.html', products=products)
    return render_template('products.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_details = request.form
        username = user_details['username']
        cursor = mysql.connection.cursor()
        result_value = cursor.execute(
            "SELECT * FROM user WHERE username = %s", ([username]))
        if result_value > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'], user_details['password']):
                session['login'] = True
                if username.lower() == 'admin':
                    session['is_admin'] = True

                return redirect('/')
            else:
                cursor.close()
                flash("Invalid credentials!", 'danger')
                return render_template('/login.html')
        else:
            cursor.close()
            flash(f"User '{user_details['username']}' not found!", 'danger')
            return render_template('/login.html')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_details = request.form
        if user_details['password'] != user_details['confirmPassword']:
            flash("Passwords do not match! Try again.", 'danger')
            return render_template('register.html')
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO user(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)",
            (
                user_details["firstname"],
                user_details["lastname"],
                user_details["username"],
                user_details["email"],
                generate_password_hash(user_details["password"]),
            ),
        )

        mysql.connection.commit()
        cursor.close()
        flash("Registration successful! Please login.", 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/product-form', methods=['GET', 'POST'])
def product_form():
    print('Session', session)
    if request.method == 'POST':
        product_details = request.form
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO product(category, product_name, quantity, price, image) VALUES (%s, %s, %s, %s, %s)",
            (
                product_details["category"],
                product_details["product_name"],
                product_details["quantity"],
                product_details["price"],
                product_details["image"]
            ),
        )

        mysql.connection.commit()
        cursor.close()
        flash("Товар добавлен!", 'success')
        # return redirect('/product-form')
    return render_template('product-form.html')


@app.route('/about')
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
