
from pymodm import fields, MongoModel


class PoemLines(MongoModel):

    datetime_added = fields.DateTimeField()
    line = fields.CharField()

    class Meta:
        connection_alias = 'poem-generator-connection'
        collection_name = 'lines'


class Poem(MongoModel):

    datetime_created = fields.DateTimeField()
    ordered_lines = fields.ListField(fields.ReferenceField(PoemLines))

    class Meta:
        connection_alias = 'poem-generator-connection'
        collection_name = 'poems'
