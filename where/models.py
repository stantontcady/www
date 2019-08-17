
from collections import deque
from csv import reader as csv_reader
from datetime import datetime
from operator import itemgetter
from typing import Iterable

from dateutil import parser as date_parser
from pandas import concat, read_csv, to_datetime
from pint import UnitRegistry
from pymodm import EmbeddedMongoModel, fields, MongoModel
from reverse_geocoder import search as reverse_geocode_search

ureg = UnitRegistry()


class ReverseGeocoding(MongoModel):
    pass


class PythonReverseGeocoding(ReverseGeocoding):

    _country_code_to_name_mapping = {
        'US': 'United States',
        'CA': 'Canada',
        'PT': 'Portugal',
        'ES': 'Spain',
        'NL': 'Netherlands',
        'IS': 'Iceland',
        'MA': 'Morocco',
        'FR': 'France'
    }

    country_code = fields.CharField(verbose_name='Country Code', mongo_name='cc', required=True)
    admin1 = fields.CharField(verbose_name='State/Province', mongo_name='a1', required=True)
    admin2 = fields.CharField(verbose_name='County/Other', mongo_name='a2', blank=True)
    name = fields.CharField()

    datetime = fields.DateTimeField(verbose_name='UTC Time', mongo_name='t', required=True)

    # we need to chunk to stay within relatively limited memory available on server
    max_chunk_size = 50000

    @property
    def country_name(self):
        return self._country_code_to_name_mapping.get(self.country_code, self.country_code)


    @classmethod
    def add_reverse_geocoding(cls, locations: Iterable):

        def create_chunk(locations):

            count = 0
            while count <= cls.max_chunk_size:

                try:
                    yield next(locations)

                except StopIteration:
                    break

                else:
                    count += 1


        def chunk_locations(locations):

            while True:

                chunked_locations = tuple(create_chunk(locations))

                if chunked_locations:
                    yield chunked_locations

                else:
                    break


        for chunked_locations in chunk_locations(locations):

            datetime_of_reverse_geocoding = datetime.now()

            for location, reverse_geocoding in zip(
                    chunked_locations,
                    reverse_geocode_search(
                        tuple((location.latitude, location.longitude) for location in chunked_locations), verbose=False
                    )
            ):

                location.reverse_geocoding = cls(
                    name=reverse_geocoding['name'],
                    admin1=reverse_geocoding['admin1'],
                    admin2=reverse_geocoding['admin2'],
                    country_code=reverse_geocoding['cc'],
                    datetime=datetime_of_reverse_geocoding
                )

                yield location


class Location(MongoModel):

    datetime = fields.DateTimeField(verbose_name='UTC Time', mongo_name='t', required=True)

    latitude = fields.FloatField(required=True, mongo_name='lat')
    longitude = fields.FloatField(required=True, mongo_name='lon')

    reverse_geocoding = fields.EmbeddedDocumentField(ReverseGeocoding, blank=True)

    class Meta:
        connection_alias = 'where-connection'
        collection_name = 'location'


class CustomLoggerLocation(Location):

    num_satellites = fields.IntegerField(verbose_name='Number of Satellites', blank=True)
    speed_knots = fields.FloatField(verbose_name='Speed [knots]', blank=True)
    track_angle_degrees = fields.FloatField(verbose_name='Track Angle [deg]', blank=True)

    sample_rate_s = 5

    @property
    def altitude(self):
        return self.altitude*ureg.meter


    @property
    def speed(self):
        return self.speed_knots*ureg.knot


    @classmethod
    def load(cls, *paths, reverse_geocoding_adder=None, check_existence=True):


        def cell_getter_factory(header_row, column_name, parser, required_column=False):

            try:
                column_index = header_row.index(column_name)

            except ValueError as exc:

                if required_column:
                    raise ValueError(
                        f'cannot create cell getter because header line in \'{path}\' does not contain'
                        f'\'{column_name}\' column'
                    ) from exc

                else:
                    return lambda row: None

            return lambda row: parser(itemgetter(column_index)(row))


        def create_location_objects(paths):

            for path in paths:

                with open(path, 'r') as source_file:

                    source_file_csv_reader = csv_reader(source_file)

                    header_row = next(source_file_csv_reader)

                    time_getter = cell_getter_factory(
                        header_row, 'time', parser=date_parser.parse, required_column=True
                    )
                    latitude_getter = cell_getter_factory(header_row, 'latitude',  parser=float, required_column=True)
                    longitude_getter = cell_getter_factory(header_row, 'longitude', parser=float, required_column=True)
                    num_satellites_getter = cell_getter_factory(header_row, 'num_satellites', parser=int)
                    speed_getter = cell_getter_factory(header_row, 'speed', parser=float)
                    angle_getter = cell_getter_factory(header_row, 'angle', parser=float)

                    for row in source_file_csv_reader:

                        datetime = time_getter(row)

                        # TODO: determine what this will do if there are datapoints from two different devices,
                        # i.e., classes, that have the same timestamp
                        if check_existence and cls.objects.raw({'t': datetime}).limit(1).count():
                            continue

                        yield cls(
                            datetime=time_getter(row),
                            latitude=latitude_getter(row),
                            longitude=longitude_getter(row),
                            num_satellites=num_satellites_getter(row),
                            speed_knots=speed_getter(row),
                            track_angle_degrees=angle_getter(row)
                        )


        reverse_geocoding_adder = PythonReverseGeocoding.add_reverse_geocoding or reverse_geocoding_adder

        for location in reverse_geocoding_adder(create_location_objects(paths)):
            location.save()

        from IPython import embed; embed()
