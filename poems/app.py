
from datetime import datetime

from flask import Flask, render_template
from flask_restful import Api as RESTFULApi, Resource, reqparse
from pymodm.connection import connect
from pymodm.errors import ValidationError

from credentials import secret_key, mongo_username, mongo_password
from models import Poem, PoemLine


app = Flask(__name__)
restful_api = RESTFULApi(app)
app.secret_key = secret_key

base_uri = f'mongodb://{mongo_username}:{mongo_password}@localhost:27017'
poems_uri = f'{base_uri}/poems?authSource=admin'
connect(poems_uri, alias='poem-generator-connection')

parser = reqparse.RequestParser()
parser.add_argument('poem_line')


class SavePoemLine(Resource):

    def put(self):

        args = parser.parse_args()

        try:
            PoemLine(value=args['poem_line'], datetime_added=datetime.now()).save()

        except ValidationError:
            return False

        else:
            return True


restful_api.add_resource(SavePoemLine, '/save_poem_line')


@app.route('/enter_line')
def enter_line():

    poem_line_query = PoemLine.objects.raw({})
    if poem_line_query.count() > 0:
        latest_poem_line = poem_line_query.order_by([('datetime_added', -1)]).first().value

    else:
        latest_poem_line = None

    return render_template('enter_line.html', latest_poem_line=latest_poem_line)


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
