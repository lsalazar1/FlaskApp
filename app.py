from flask import Flask, render_template, flash, redirect,\
     url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField,\
     PasswordField, validators
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

# Home page
@app.route('/')
def index():
    return render_template('home.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Homework logger
@app.route('/assignments')
def homework():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get assignments from DB
    results = cur.execute("SELECT * FROM assignments")

    assignments = cur.fetchall()


    if results > 0:
        return render_template('assignments.html', assignments = assignments)
    else:
        msg = "No assignments found"
        return render_template('assignments.html', msg = msg)
    
    # Close cur connection
    cur.close()


# Specific Assignments
@app.route('/assignment/<string:id>/')
def assignment(id):
    # Create cursor
    cur = mysql.connection.cursor()

     # Get assignments from DB
    results = cur.execute("SELECT * FROM assignments WHERE id = %s", [id])
    assignment = cur.fetchone()

    return render_template('assignment.html', assignment=assignment)

# Registration page
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

        flash("Welcome! Thanks for registering!", 'success')

    
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
                session['uid'] = data['uid']

                flash("Hello, you are now logged in", 'success')
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
            flash("Unauthorized access" , 'danger')
            return redirect(url_for('login'))
    return wrap

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get assignments from DB
    results = cur.execute("SELECT * FROM assignments")

    assignments = cur.fetchall()


    if results > 0:
        return render_template('dashboard.html', assignments = assignments)
    else:
        msg = "No assignments found"
        return render_template('dashboard.html', msg = msg)
    
    # Close cur connection
    cur.close()
    
# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')

    return redirect(url_for('login'))

# Add Assignment
@app.route("/add_assignment", methods = ['GET', 'POST'])
@is_logged_in
def add_assignment():
    form = AssignmentForm(request.form)
    if request.method == 'POST' and form.validate():
        assignment = form.assignment.data
        course = form.course.data
        dueDate = form.dueDate.data
        description = form.description.data

        # Create MySQL Cursor
        cur = mysql.connection.cursor()

        # Execute cur commands
        cur.execute("INSERT INTO assignments(assignmentName, course, dueDate, description, uid) VALUES(%s, %s, %s, %s, %s)",\
         (assignment, course, dueDate, description, session['uid']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Assignment has been added', 'success')

        return redirect(url_for('dashboard'))
    
    return render_template('add_assignment.html', form=form)

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

# Assignment Form Class
class AssignmentForm(Form):
    assignment = StringField('Assignment Name', [validators.length(min=1, max=50)])
    course = StringField('Course Name (Ex. COMP3333)', [validators.length(min=1,max=9)])
    dueDate = StringField('Due Date (Ex. YYYY-MM-DD)', [validators.length(min=1)])
    description = StringField('Description', [validators.length(min=1)])

# Runs the Code
if __name__ == '__main__' :
    app.secret_key = 'password'
    app.run(debug=True)