
from collections import deque
from datetime import datetime
from typing import Iterable

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
    admin2 = fields.CharField(verbose_name='County/Other', mongo_name='a2', required=True)
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
    def load(cls, *paths, add_reverse_geocoding=None):

        def create_location_objects(data):

            for row in data.itertuples(index=False):
                yield cls(
                    datetime=row.timestamp,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    num_satellites=row.num_satellites,
                    speed_knots=row.speed,
                    track_angle_degrees=row.angle
                )


        def to_dataframe(paths):

            def helper():
                for path in paths:

                    dataframe = read_csv(path)
                    dataframe['timestamp']= to_datetime(dataframe.time)

                    yield dataframe


            return concat(helper(), ignore_index=True)


        add_reverse_geocoding = PythonReverseGeocoding.add_reverse_geocoding or add_reverse_geocoding

        new_locations = deque(add_reverse_geocoding(create_location_objects(to_dataframe(paths))), maxlen=50000)

        from IPython import embed; embed()
        # for entry, reverse_geocode_result in zip(new_locations, reverse_geocode_locations(*new_locations)):
        #
        #     entry.reverse_geocoding = PythonReverseGeocoding(
        #         country_code=reverse_geocode_result['cc'],
        #         admin1=reverse_geocode_result['admin1'],
        #         admin2=reverse_geocode_result['admin2'],
        #         name=reverse_geocode_result['name']
        #     )
        #
        # cls.objects.bulk_create(new_entries)
