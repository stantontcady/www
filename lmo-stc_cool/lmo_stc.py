
from datetime import datetime
from operator import ge, le
from pytz import timezone

from bson.objectid import ObjectId
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_restful import Api as RESTFULApi, Resource, reqparse
from pymodm.connection import connect
from pymodm.errors import ValidationError

from credentials import admin_key, secret_key, mongo_username, mongo_password
from rsvp_model import RSVP


app = Flask(__name__)
restful_api = RESTFULApi(app)
Bootstrap(app)

app.secret_key = secret_key

base_uri = f'mongodb://{mongo_username}:{mongo_password}@localhost:27017'
wedding_uri = f'{base_uri}/wedding?authSource=admin'
connect(wedding_uri, alias='wedding-connection')

parser = reqparse.RequestParser()
parser.add_argument('key')
parser.add_argument('value')
parser.add_argument('name')
parser.add_argument('dietary_name')
parser.add_argument('email_address')
parser.add_argument('suggested_songs')
parser.add_argument('guest_name')
parser.add_argument('which_brunch')

eastern_timezone = timezone('US/Eastern')


class GetRSVPMixin:

    @staticmethod
    def _get_rsvp(rsvp_id):

        matched_rsvps = tuple(RSVP.objects.raw({'_id': ObjectId(rsvp_id)}))

        if matched_rsvps:
            return matched_rsvps[0]

        else:
            return None


class UpdateBoolField(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        rsvp = self._get_rsvp(rsvp_id)

        if rsvp is not None:

            args = parser.parse_args()

            try:
                value = bool(int(args['value']))
            except (TypeError, ValueError):
                return False

            setattr(rsvp, args['key'], value)

            rsvp.save_parameter()
            return {'last_saved': rsvp.formatted_last_saved}

        return False


class UpdateDietaryRestrictions(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        args = parser.parse_args()

        try:
            value = bool(int(args['value']))

        except (TypeError, ValueError):
            return False

        if args['name'] == 'guest':
            result = RSVP.objects.raw(
                {'_id': ObjectId(rsvp_id)}
            ).update({'$set': {f'guest.{args["dietary_name"]}': value}})

        else:
            result = RSVP.objects.raw(
                {'_id': ObjectId(rsvp_id), 'people.name': args['name']}
            ).update({'$set': {f'people.$.{args["dietary_name"]}': value}})

        if result != 0:

            rsvp = self._get_rsvp(rsvp_id)
            rsvp.save_parameter()

            return {'last_saved': rsvp.formatted_last_saved}

        return False


class UpdateEmailAddress(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        args = parser.parse_args()

        rsvp = self._get_rsvp(rsvp_id)

        if rsvp is not None:

            email_address = args['email_address']

            if not email_address:
                rsvp.email_address = None

            else:
                rsvp.email_address = email_address

            try:
                rsvp.save_parameter()

            except ValidationError:
                pass

            else:
                return {'last_saved': rsvp.formatted_last_saved}

        return False


class UpdateSuggestedSongs(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        args = parser.parse_args()

        rsvp = self._get_rsvp(rsvp_id)

        if rsvp is not None:

            rsvp.suggested_songs = args['suggested_songs']
            try:
                rsvp.save_parameter()

            except ValidationError:
                pass

            else:
                return {'last_saved': rsvp.formatted_last_saved}

        return False


class UpdateGuestName(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        args = parser.parse_args()

        result = RSVP.objects.raw({'_id': ObjectId(rsvp_id)}).update({'$set': {'guest.name': args['guest_name']}})

        if result != 0:

            rsvp = self._get_rsvp(rsvp_id)
            rsvp.save_parameter()

            return {'last_saved': rsvp.formatted_last_saved, 'names_of_people_in_party': rsvp.names_of_people_in_party}

        return False


class UpdateDietaryOther(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        args = parser.parse_args()

        value = args['value']
        if not value:
            value = None

        if args['name'] == 'guest':
            result = RSVP.objects.raw(
                {'_id': ObjectId(rsvp_id)}
            ).update({'$set': {f'guest.dietary_other': value}})

        else:
            result = RSVP.objects.raw(
                {'_id': ObjectId(rsvp_id), 'people.name': args['name']}
            ).update({'$set': {f'people.$.dietary_other': value}})

        if result != 0:

            rsvp = self._get_rsvp(rsvp_id)
            rsvp.save_parameter()

            return {'last_saved': rsvp.formatted_last_saved}

        return False


class UpdateSundayBrunch(GetRSVPMixin, Resource):

    def put(self, rsvp_id):

        rsvp = self._get_rsvp(rsvp_id)

        if rsvp is not None:

            args = parser.parse_args()

            rsvp.which_brunch = args['which_brunch']
            rsvp.save()

            return True

        return False


restful_api.add_resource(UpdateBoolField, '/update_bool_field/<rsvp_id>')
restful_api.add_resource(UpdateDietaryRestrictions, '/update_dietary_restrictions/<rsvp_id>')
restful_api.add_resource(UpdateEmailAddress, '/update_email_address/<rsvp_id>')
restful_api.add_resource(UpdateSuggestedSongs, '/update_suggested_songs/<rsvp_id>')
restful_api.add_resource(UpdateGuestName, '/update_guest_name/<rsvp_id>')
restful_api.add_resource(UpdateDietaryOther, '/update_dietary_other/<rsvp_id>')
restful_api.add_resource(UpdateSundayBrunch, '/update_sunday_brunch/<rsvp_id>')


def get_rsvp_from_url_path(rsvp_url_path):

    matched_rsvps = tuple(RSVP.objects.raw({'url_paths': rsvp_url_path}))

    if matched_rsvps:
        if len(matched_rsvps) > 1:
            return None

        return matched_rsvps[0]

    else:
        return None


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/<rsvp_url_path>')
def rsvp(rsvp_url_path):

    rsvp = get_rsvp_from_url_path(rsvp_url_path.casefold())

    if rsvp is not None:
        try:
            key = request.args.get('key')
        except Exception:
            key = None

        if key is None or key != admin_key:
            rsvp.last_seen = datetime.now()
            rsvp.save()

        return render_template(
            'rsvp.html',
            rsvp=rsvp,
            show_favors_link=ge(
                datetime.now(eastern_timezone), datetime(2019, 9, 29, 7, 30, 0, tzinfo=eastern_timezone)
            ),
            ceremony_rehearsal=set(
                rsvp.url_paths
            ).intersection(
                ('milano', 'slo&smello', 'chiefmoyofficer', 'steve&beth', 'steph&josh')
            ),
            allow_sunday_breakfast_schedule_change=le(
                datetime.now(eastern_timezone), datetime(2019, 9, 27, 15, 0, 0, tzinfo=eastern_timezone)
            )
        )

    else:
        return render_template('error.html', rsvp_url_path=rsvp_url_path)


@app.route('/view_rsvps/<key>')
def view_rsvps(key):

    if key == admin_key:
        return render_template('view_rsvps.html', rsvps=tuple(RSVP.objects.all()), key=key, rsvp_class=RSVP)


@app.route('/view_rsvps/<key>/<event_name>')
def view_rsvps_by_event(key, event_name):

    if key == admin_key:

        event_name_to_display_name_mapping = {
            'friday_hike': 'Friday Acadia Visit',
            'friday_dinner': 'Friday Dinner at Barncastle Restaurant',
            'friday_bonfire': 'Friday Bonfire at The Lookout',
            'saturday_activity': 'Saturday Osgood Trail Hike',
            'sunday_brunch': 'Sunday Brunch'
        }
        return render_template(
            'view_rsvps.html',
            rsvps=tuple(RSVP.get_parties_that_accepted_event(event_name)),
            key=key,
            rsvp_class=RSVP,
            event_name=event_name,
            event_display_name=event_name_to_display_name_mapping[event_name]
        )


@app.route('/acadia')
def view_acadia_schedule():
    return render_template('acadia.html')


@app.route('/menu')
def view_menu():
    return render_template('menu.html')


@app.route('/favors/<rsvp_url_path>')
def view_party_favors(rsvp_url_path):

    rsvp = get_rsvp_from_url_path(rsvp_url_path.casefold())

    if rsvp is not None:
        state_o_maine_image_path = f'img/state_o_maine_pages/{rsvp.url_paths[0]}.png'
        return render_template('party_favors.html', rsvp=rsvp, state_o_maine_image_path=state_o_maine_image_path)

    return render_template('error.html', rsvp_url_path=rsvp_url_path)


@app.route('/sunday_breakfast/<rsvp_url_path>')
def view_sunday_breakfast(rsvp_url_path):

    rsvp = get_rsvp_from_url_path(rsvp_url_path.casefold())

    if rsvp is not None:

        other_rsvps_in_first_time_slot = list(RSVP.objects.raw({'which_brunch': 'first'}))

        try:
            other_rsvps_in_first_time_slot.remove(rsvp)
        except ValueError:
            pass

        other_rsvps_in_second_time_slot = list(RSVP.objects.raw({'which_brunch': 'second'}))

        try:
            other_rsvps_in_second_time_slot.remove(rsvp)
        except ValueError:
            pass

        return render_template(
            'sunday_breakfast.html',
            rsvp=rsvp,
            other_rsvps_in_first_time_slot=other_rsvps_in_first_time_slot,
            other_rsvps_in_second_time_slot=other_rsvps_in_second_time_slot,
            max_people_per_time_slot=26
        )

    return render_template('error.html', rsvp_url_path=rsvp_url_path)

@app.route('/kayaks')
def view_kayak_guidelines():
    return render_template('kayak_guidelines.html')
