
from pymodm import fields, MongoModel


class PoemLine(MongoModel):

    datetime_added = fields.DateTimeField()
    value = fields.CharField()

    class Meta:
        connection_alias = 'poem-generator-connection'
        collection_name = 'lines'


class Poem(MongoModel):

    datetime_created = fields.DateTimeField()
    ordered_lines = fields.ListField(fields.ReferenceField(PoemLine))

    class Meta:
        connection_alias = 'poem-generator-connection'
        collection_name = 'poems'
