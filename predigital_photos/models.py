
from pymodm import EmbeddedMongoModel, fields, MongoModel


class PreDigitalPhoto(MongoModel):

    datetime_added = fields.DateTimeField()

    front_reproductions = fields.ListField(fields.ImageField(), blank=True)
    back_reproductions = fields.ListField(fields.ImageField(), blank=True)

    front_marking = fields.CharField(blank=True)
    back_marking = fields.CharField(blank=True)

    fuzzy_location = fields.EmbeddedModelField(FuzzyLocation, blank=True)
    fuzzy_datetime = fields.EmbeddedModelField(FuzzyDateTime, blank=True)

    notes = fields.EmbeddedModelListField(PreDigitalPhotoNote, blank=True)

    people = fields.ListField(fields.ReferenceField(Person), blank=True)

    class Meta:
        connection_alias = 'pre-digital-photos-connection'
        collection_name = 'photos'


class Person(MongoModel):

    first_name = fields.CharField(blank=True)
    last_name = fields.CharField(blank=True)

    class Meta:
        connection_alias = 'pre-digital-photos-connection'
        collection_name = 'people'


class PreDigitalPhotoNote(EmbeddedMongoModel):

    datetime_added = fields.DateTimeField()
    added_by_name = fields.CharField()
    source = fields.CharField()
    content = fields.CharField()


class FuzzyDateTime(EmbeddedMongoModel):
    qualitative_time = fields.CharField(blank=True)
    source = fields.CharField(required=True)


class CircaYearFuzzyDate(FuzzyDateTime):

    earliest_year = fields.IntegerField(blank=True)
    latest_year = fields.IntegerField(blank=True)


class HolidayCircaYearFuzzyDate(CircaYearFuzzyDate):
    holiday_name = fields.CharField(required=True)


class KnownYearFuzzyDate(FuzzyDateTime):
    year = fields.IntegerField(required=True)


class KnownMonthFuzzyDate(FuzzyDateTime):
    month = fields.IntegerField(required=True)


class KnownMonthAndYearFuzzyDate(KnownMonthFuzzyDate, KnownYearFuzzyDate):
    pass


class FuzzyLocation(EmbeddedMongoModel):
    address = fields.CharField(blank=True)
    description = fields.CharField(blank=True)
    source = fields.CharField(required=True)


class FuzzyUSLocation(FuzzyLocation):
    city = fields.CharField(blank=True)
    state = fields.CharField(blank=True)


class FuzzyAbroadLocation(FuzzyLocation):
    country = fields.CharField(blank=True)


class PreDigitalPhotoCollection(MongoModel):

    datetime_added = fields.DateTimeField()
    name = fields.CharField(required=True)
    description = fields.CharField(blank=True)
    contents = fields.ListField(field.ReferenceField(PreDigitalPhoto))
