
from pymodm import EmbeddedMongoModel, fields, MongoModel


class Recipe(MongoModel):

    ingredients = fields.EmbeddedModelListField(Ingredient)

    source = fields.EmbeddedModelField(RecipeSource)

    notes = fields.ListField(Note)

    tags = fields.EmbeddedModelListField(Tag)

    instructions = fields.CharField()


class Ingredient(EmbeddedMongoModel):

    name = fields.CharField()
    amount = fields.FloatField()
    unit = fields.CharField()

    notes = fields.ListField(Note)

    classification = fields.CharField(choices=('wet', 'dry', 'other', 'n/a'))


class RecipeSource(EmbeddedMongoModel):

    name = fields.CharField()

    url = fields.URLField()

    image = fields.ImageField()


class Note(EmbeddedMongoModel):

    added_by = fields.ReferenceField(User)

    content = fields.CharField()

    datetime_added = fields.DateTimeField()


class Tag(EmbeddedMongoModel):

    added_by = fields.ReferenceField(User)

    content = fields.CharField()

    datetime_added = fields.DateTimeField()


class RecipeActualization(MongoModel):

    photos = fields.ListField(fields.ImageField())

    date_made = fields.DateTimeField()

    note_content = fields.CharField()

    made_by = fields.ReferenceField(User)


class User(MongoModel):

    name = fields.CharField()

    favorite_recipes = fields.ListField(fields.ReferenceField(Recipe))

    recipes_made = fields.ListField(fields.ReferenceField(Recipe))
