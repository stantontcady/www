
from datetime import datetime
from pymodm import fields, EmbeddedMongoModel, MongoModel
from pytz import timezone, UTC


class Person(EmbeddedMongoModel):

    name = fields.CharField(blank=True)

    dietary_vegetarian = fields.BooleanField(default=False)
    dietary_gluten_free = fields.BooleanField(default=False)
    dietary_other = fields.CharField(blank=True)


class RSVP(MongoModel):

    url_paths = fields.ListField(fields.CharField(), required=True)

    last_seen = fields.DateTimeField(blank=True)
    last_saved = fields.DateTimeField(blank=True)

    email_address = fields.EmailField(blank=True)

    people = fields.ListField(fields.EmbeddedDocumentField(Person))
    guest = fields.EmbeddedDocumentField(Person, blank=True)

    which_schedule = fields.CharField(default='friends')
    which_lodging = fields.CharField(default='other')

    accept = fields.BooleanField(blank=True)
    friday_hike = fields.BooleanField(default=False)
    friday_dinner = fields.BooleanField(default=False)
    friday_bonfire = fields.BooleanField(default=False)
    saturday_activity = fields.BooleanField(default=False)
    sunday_brunch = fields.BooleanField(default=False)

    suggested_songs = fields.CharField(mongo_name='songs', blank=True)

    class Meta:
        connection_alias = 'wedding-connection'
        collection_name = 'rsvp'


    def save_parameter(self, *args, **kwargs):
        self.last_saved = datetime.now()
        return super().save(*args, **kwargs)


    @property
    def names_of_people_in_party(self):

        def names_of_people_plus_guest():

            for person in self.people:
                yield person.name

            if self.guest:
                if self.guest.name:
                    yield self.guest.name

                else:
                    yield 'Guest'

        names = tuple(names_of_people_plus_guest())

        if len(names) < 3:
            return ' and '.join(names)

        else:
            return ', '.join(names[:-1]) + ', and ' + names[-1]


    @property
    def formatted_last_saved(self):
        return self.last_saved.replace(
            tzinfo=UTC
        ).astimezone(timezone('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p %Z')
