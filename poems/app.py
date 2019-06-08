
from datetime import datetime
from random import randint

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
        latest_poem_line = next(poem_line_query.order_by([('datetime_added', -1)]))

    else:
        latest_poem_line = None

    return render_template('enter_line.html', latest_poem_line=latest_poem_line)


@app.route('/new/<poem_type>')
def generate_and_show_poem(poem_type):

    if poem_type == "sonnet":

        poem_line_query = PoemLine.objects.raw({})

        if poem_line_query.count() > 14:

            all_poem_lines = tuple(poem_line_query)

            selected_value_to_poem_line_mapping = {}
            while len(selected_value_to_poem_line_mapping) < 15:
                random_line = all_poem_lines[randint(0, poem_line_query.count() -1)]
                if random_line.value not in selected_value_to_poem_line_mapping:
                    selected_value_to_poem_line_mapping[random_line.value] = random_line

            new_poem = Poem(
                ordered_lines=list(selected_value_to_poem_line_mapping.values()), datetime_created=datetime.now()
            )
            new_poem.save()

            return render_template('view_poem.html', poem=new_poem)

    return render_template('view_poem.html', poem=None)


@app.route('/previous')
def show_previous_poem():
    return render_template('view_poems.html', poems=Poem.objects.raw({}))
