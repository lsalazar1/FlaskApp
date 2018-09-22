from flask import Flask, render_template
from data import Homework

app = Flask(__name__)

Homework = Homework()

#routes to homepage
@app.route('/')
def index():
    return render_template('home.html')

#routes to about page
@app.route('/about')
def about():
    return render_template('about.html')

#routes to homework page
#CRUD operations used here later
@app.route('/homework')
def homework():
    return render_template('homework.html', homework = Homework)

#routes to assignment's specific webpage
@app.route('/assignment/<string:id>/')
def assignment(id):
    return render_template('assignment.html', id=id)


if __name__ == '__main__' :
    app.run(debug=True)