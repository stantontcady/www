
from flask import Flask, render_template
from pymodm.connection import connect

from credentials import secret_key, mongo_username, mongo_password
from models import Poem, PoemLines


app = Flask(__name__)

app.secret_key = secret_key

base_uri = f'mongodb://{mongo_username}:{mongo_password}@localhost:27017'
poems_uri = f'{base_uri}/poems?authSource=admin'
connect(poems_uri, alias='poem-generator-connection')


@app.route('/enter_line')
def enter_line():
    return render_template('enter_line.html')


@app.route('/new')
def generate_and_show_poem():
    # poem = random_generator
    # add to Poem collection
    poem = None
    return render_template('view_poem.html', poem=poem)


@app.route('/previous')
def show_previous_poem():
    # get random poem from Poem collection
    poem = None
    return render_template('view_poem.html', poem=poem)
