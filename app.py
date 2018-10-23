from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Homework
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# MySQL initializing...
mysql = MySQL(app)

Homework = Homework()

# Home page
@app.route('/')
def index():
    return render_template('home.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Homework logger
@app.route('/homework')
def homework():
    return render_template('homework.html', homework = Homework)


# Specific Assignments
@app.route('/assignment/<string:id>/')
def assignment(id):
    return render_template('assignment.html', id=id)

#Registration page
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    # When user request method is post do this ...
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor to input MySQL commands using user's info
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to database
        mysql.connection.commit()

        # Close MySQL
        cur.close()

        flash('Welcome! Thanks for registering!', 'success')

    
        return redirect(url_for('login'))

    return render_template('register.html', form = form)

# User login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # Get form fields
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        # Create MySQL Cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                #Successful login
                session['logged_in'] = True
                session['username'] = username

                flash('Hello there!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Incorrect Password'
                return render_template('login.html', error=error)
            # Close MySQL connection
            cur.close()

        else:
            error = "No users with that username found"
            return render_template('login.html', error=error)
    
    return render_template('login.html')

# Authenticates if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You don't have access yet! Please login!" , 'danger')
            return redirect(url_for('login'))
    return wrap

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')
    
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')

    return redirect(url_for('login'))

# Register Form Class
class RegistrationForm(Form):
    name = StringField('Name', [validators.length(min = 1, max = 50)])
    username = StringField('Username', [validators.length(min = 2, max = 30)])
    email = StringField('Email', [validators.length(min=3, max=100)])
    password = StringField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


if __name__ == '__main__' :
    app.secret_key = 'password'
    app.run(debug=True)