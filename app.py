from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import Homework
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

Homework = Homework()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/homework')
def homework():
    return render_template('homework.html', homework = Homework)

@app.route('/assignment/<string:id>/')
def assignment(id):
    return render_template('assignment.html', id=id)

#Registration page
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    #checks if request method is post or get
    if request.method == 'POST' and form.validate():
        return render_template('register.html')

    return render_template('register.html', form = form)

class RegistrationForm(Form):
    name = StringField('Name', [validators.length(min = 1, max = 50)])
    username = StringField('Username', [validators.length(min = 2, max = 30)])
    email = StringField('Email', [validators.length(min=3, max=100)])
    password = StringField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Cofirm Password')


if __name__ == '__main__' :
    app.run(debug=True)