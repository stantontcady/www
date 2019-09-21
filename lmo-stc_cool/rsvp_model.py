
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

    which_brunch = fields.CharField(blank=True)

    suggested_songs = fields.CharField(mongo_name='songs', blank=True)

    class Meta:
        connection_alias = 'wedding-connection'
        collection_name = 'rsvp'


    def save_parameter(self, *args, **kwargs):
        self.last_saved = datetime.now()
        return super().save(*args, **kwargs)


    @classmethod
    def get_parties_that_accepted(cls):
        return cls.objects.raw({'accept': True})


    @classmethod
    def get_num_parties_that_accepted(cls):
        return cls.get_parties_that_accepted().count()


    @classmethod
    def get_parties_that_declined(cls):
        return cls.objects.raw({'accept': False})


    @classmethod
    def get_num_parties_that_declined(cls):
        return cls.get_parties_that_declined().count()


    @classmethod
    def get_num_people_in_parties(cls, rsvps):
        return sum(rsvp.num_people_in_party for rsvp in rsvps)


    

    @classmethod
    def get_parties_that_accepted_event(cls, event_name):
        return cls.objects.raw({event_name: True})


    @classmethod
    def get_num_parties_that_accepted_event(cls, event_name):
        return cls.get_parties_that_accepted_event(event_name).count()


    @classmethod
    def get_vegetarian_people(cls):

        def helper():

            for rsvp in cls.objects.raw({'people.dietary_vegetarian': True}):
                for person in rsvp.people:
                    if person.dietary_vegetarian:
                        yield person

            for rsvp in cls.objects.raw({'guest.dietary_vegetarian': True}):
                if rsvp.guest.dietary_vegetarian:
                    yield rsvp.guest


        return tuple(helper())


    @classmethod
    def get_gluten_free_people(cls):

        def helper():

            for rsvp in cls.objects.raw({'people.dietary_gluten_free': True}):
                for person in rsvp.people:
                    if person.dietary_gluten_free:
                        yield person

            for rsvp in cls.objects.raw({'guest.dietary_gluten_free': True}):
                if rsvp.guest.dietary_gluten_free:
                    yield rsvp.guest


        return tuple(helper())


    @classmethod
    def get_other_dietary_restrictions_people(cls):

        def helper():

            for rsvp in cls.objects.raw({'people.dietary_other': {"$ne": None}}):
                for person in rsvp.people:
                    if person.dietary_other is not None:
                        yield person, person.dietary_other

            for rsvp in cls.objects.raw({'guest.dietary_other': {"$ne": None}}):
                if rsvp.guest.dietary_other is not None:
                    yield rsvp.guest, person.dietary_other


        return tuple(helper())


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
    def num_people_in_party(self):

        num_people = len(self.people)

        if self.guest is not None and self.guest.name is not None:
            num_people += 1

        return num_people


    @property
    def formatted_last_saved(self):
        return self.last_saved.replace(
            tzinfo=UTC
        ).astimezone(timezone('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p %Z')
