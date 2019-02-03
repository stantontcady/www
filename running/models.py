
from fitparse import FitFile
from pint import UnitRegistry
from pymodm import EmbeddedMongoModel, fields, MongoModel
from reverse_geocoder import search as reverse_geocode_search

ureg = UnitRegistry()


class BodyWeight(MongoModel):

    value_lbs = fields.FloatField(mongo_name='lbs', required=True)
    time = fields.DateTimeField(required=True)

    @property
    def value(self):
        return self.value_lbs*ureg.pound


    class Meta:
        connection_alias = 'health-connection'
        collection_name = 'body_weight'


class Shoes(MongoModel):

    color = fields.CharField(required=True)
    brand = fields.CharField(required=True)
    short_name = fields.CharField(required=True)

    purchase_date = fields.DateTimeField(mongo_name='purchase_dt', required=True)
    purchase_price = fields.FloatField(mongo_name='price', required=True)
    purchase_merchant = fields.CharField(mongo_name='purchased_from', required=True)

    class Meta:
        connection_alias = 'gear-connection'
        collection_name = 'shoes'


class Device(MongoModel):

    purchase_date = fields.DateTimeField(mongo_name='purchase_dt', required=True)
    purchase_price = fields.FloatField(mongo_name='price', required=True)

    manufacturer = fields.CharField(verbose_name='Manufacturer', required=True)
    name = fields.CharField(verbose_name='Device Variable Name', required=True)
    display_name = fields.CharField(verbose_name='Device Name', required=True)

    serial_number = fields.CharField(verbose_name='Serial #', required=True)

    # product_photo = fields.ImageField()

    class Meta:
        connection_alias = 'gear-connection'
        collection_name = 'devices'


class Location(MongoModel):

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

    latitude = fields.FloatField(mongo_name='lat', required=True)
    longitude = fields.FloatField(mongo_name='lon', required=True)

    time = fields.DateTimeField(verbose_name='UTC Time', mongo_name='t', required=True)

    country_code = fields.CharField(verbose_name='Country Code', mongo_name='cc', required=True)
    admin1 = fields.CharField(verbose_name='State/Province', mongo_name='a1', required=True)
    admin2 = fields.CharField(verbose_name='County/Other', mongo_name='a2', required=True)
    name = fields.CharField()

    modality = fields.CharField(
        choices=('unknown', 'run', 'bike', 'car', 'plane', 'boat', 'train', 'stationary', 'walking'),
        default='unknown'
    )

    device = fields.ReferenceField(Device)

    @property
    def country_name(self):
        return self._country_code_to_name_mapping.get(self.country_code, self.country_code)


    class Meta:
        connection_alias = 'location-connection'
        collection_name = 'data'


class LocationWhileRunning(Location):

    altitude_m = fields.FloatField(mongo_name='alt_m', verbose_name='Altitude [m]', blank=True)
    speed_m_s = fields.FloatField(verbose_name='Speed [m/s]', blank=True)
    vertical_oscillation_mm = fields.FloatField(
        mongo_name='vert_osc_mm', verbose_name='Vertical Oscillation [mm]', blank=True
    )
    ground_contact_time_ms = fields.FloatField(
        mongo_name='gct_ms', verbose_name='Ground Contact Time [ms]', blank=True
    )
    power_w = fields.FloatField(verbose_name='Power [W]', blank=True)
    heart_rate_bpm = fields.IntegerField(mongo_name='hr_bpm', verbose_name='Heart Rate [bpm]', blank=True)
    temperature_c = fields.IntegerField(mongo_name='temp_c', verbose_name='Temperature [C]', blank=True)
    step_length_mm = fields.FloatField(verbose_name='Step Length [mm]', blank=True)
    ground_contact_time_balance = fields.FloatField(
        verbose_name='Ground Contact Time Balance %', mongo_name='gct_bal', blank=True
    )
    cadence_steps_min = fields.IntegerField(
        verbose_name='Running Cadence [strides/min]', mongo_name='running_cadence', blank=True
    )
    vertical_ratio = fields.FloatField(verbose_name='Vertical Ratio %', mongo_name='vert_ratio', blank=True)

    @property
    def altitude(self):
        return self.altitude_m*ureg.meter


    @property
    def speed(self):
        return self.speed_m_s*ureg.meter/ureg.second


    @property
    def vertical_oscillation(self):
        return self.vertical_oscillation_mm*ureg.millimeter


    @property
    def ground_contact_time(self):
        return self.ground_contact_time_ms*ureg.milliseconds


    @property
    def power_w(self):
        return self.power_w*ureg.watt


    @property
    def temperature(self):
        return Quantity(self.temperature_c, ureg.degC)


    @property
    def step_length(self):
        return self.step_length_mm*ureg.millimeter


class RunningRace(EmbeddedMongoModel):

    name = fields.CharField(verbose_name='Race Name', required=True)
    distance_name = fields.CharField(
        verbose_name='Distance Description',
        choices=('1 mile', '5k', '10k', '15k', 'half marathon', 'marathon'),
        required=True
    )
    distance_m = fields.FloatField(verbose_name='Distance [m]', required=True)
    chip_time_s = fields.FloatField(verbose_name='Chip Time [s]', mongo_name='ct_s', required=True)
    gun_time_s = fields.FloatField(verbose_name='Gun Time [s]', mongo_name='gt_s', required=True)
    splits_s = fields.DictField()

    overall_place = fields.IntegerField(verbose_name='Overall Place', required=True)
    overall_field_size = fields.IntegerField(verbose_name='Size of Overall Field', required=True)
    detailed_place = fields.DictField()

    # photos = fields.ListField(fields.ImageField(), default=[])
    supporting_files = fields.ListField(fields.FileField(), default=[])

    @property
    def distance(self):
        return self.distance_m*ureg.meter


    @property
    def chip_time(self):
        return self.chip_time_s*ureg.second


    @property
    def gun_time(self):
        return self.gun_time_s*ureg.second


    @property
    def splits(self):
        return {split_name: split_time_s*uref.second for split_name, split_time_s in self.splits_s.items()}


    @property
    def overall_place_percent(self):
        return round(100*self.overall_place/float(self.overall_field_size), 1)


class Activity(MongoModel):

    start_time = fields.DateTimeField(verbose_name='Start Time', mongo_name='start_dt')
    total_time_s = fields.FloatField(verbose_name='Total Time [s]', mongo_name='time_s')
    total_distance_m = fields.FloatField(verbose_name='Total Distance [m]', mongo_name='distance_m')

    calories_cal = fields.IntegerField(verbose_name='Calories', mongo_name='cal')
    avg_speed_m_s = fields.FloatField(verbose_name='Average Speed [m/s]')
    max_speed_m_s = fields.FloatField(verbose_name='Maximum Speed [m/s]')
    total_ascent_m = fields.IntegerField(verbose_name='Total Ascent [m]', mongo_name='ascent_m')
    total_descent_m = fields.IntegerField(verbose_name='Total Descent [m]', mongo_name='descent_m')
    avg_heart_rate_bpm = fields.IntegerField(verbose_name='Average Heart Rate [bpm]', mongo_name='avg_hr_bpm')
    max_heart_rate_bpm = fields.IntegerField(verbose_name='Maximum Heart Rate [bpm]', mongo_name='max_hr_bpm')

    aerobic_training_effect = fields.FloatField(verbose_name='Aerobic Training Effect', mongo_name='aerobic_t_e')
    anaerobic_training_effect = fields.FloatField(verbose_name='Anaerobic Training Effect', mongo_name='anaerobic_t_e')

    avg_temperature_c = fields.IntegerField(verbose_name='Average Temperature [C]', mongo_name='avg_temp_c')
    max_temperature_c = fields.IntegerField(verbose_name='Maximum Temperature [C]', mongo_name='max_temp_c')

    start_body_weight_measurment = fields.ReferenceField(BodyWeight)
    end_body_weight_measurment = fields.ReferenceField(BodyWeight)

    device = fields.ReferenceField(Device)

    start_location = fields.ReferenceField(Location)

    source_file = fields.FileField()

    commute = fields.BooleanField(default=False)

    class Meta:
        connection_alias = 'activity-connection'
        collection_name = 'data'


    @property
    def total_time(self):
        return self.total_time_s*ureg.second


    @property
    def total_distance(self):
        return self.total_distance_m*ureg.meter


    @property
    def calories(self):
        return self.calories_cal*ureg.calorie


    @property
    def avg_speed(self):
        return self.avg_speed_m_s*ureg.meter/ureg.second


    @property
    def max_speed(self):
        return self.max_speed_m_s*ureg.meter/ureg.second


    @property
    def total_ascent(self):
        return self.total_ascent_m*ureg.meter


    @property
    def total_descent(self):
        return self.total_descent_m*ureg.meter


    @property
    def avg_temperature(self):
        return ureg.Quantity(self.avg_temperature_c, ureg.degC)


    @property
    def max_temperature(self):
        return ureg.Quantity(self.max_temperature_c, ureg.degC)


    @property
    def source_file_as_fit(self):

        self.source_file.open()
        fit_file = FitFile(b''.join(self.source_file.file.chunks()))
        self.source_file.close()

        return fit_file


    @property
    def start_body_weight(self):
        return self.start_body_weight_measurment.value


    @property
    def end_body_weight(self):
        return self.end_body_weight_measurment.value


    @property
    def avg_body_weight(self):
        return 0.5*(self.start_body_weight+self.end_body_weight)


class RunningActivity(Activity):

    shoes = fields.ReferenceField(Shoes)

    avg_power_w = fields.IntegerField(verbose_name='Average Power (Estimate) [W]')
    avg_cadence_steps_min = fields.IntegerField(
        verbose_name='Average Running Cadence [strides/min]', mongo_name='avg_running_cadence'
    )
    total_num_steps = fields.IntegerField(verbose_name='Total Number of Steps', mongo_name='num_steps')
    avg_vertical_oscillation_mm = fields.FloatField(
        verbose_name='Average Vertical Oscillation [mm]', mongo_name='avg_vert_osc_mm'
    )
    avg_vertical_ratio = fields.FloatField(verbose_name='Average Vertical Ratio %', mongo_name='avg_vert_ratio')
    avg_ground_contact_time_ms = fields.FloatField(
        verbose_name='Average Ground Contact Time [ms]', mongo_name='avg_gct_ms'
    )
    avg_ground_contact_time_balance = fields.FloatField(
        verbose_name='Average Ground Contact Time Balance %', mongo_name='avg_gct_bal'
    )
    avg_step_length_mm = fields.FloatField(verbose_name='Average Step Length [mm]')

    race = fields.EmbeddedDocumentField(RunningRace)

    records = fields.ListField(fields.ReferenceField(LocationWhileRunning))

    @property
    def avg_power(self):
        return self.avg_power_w*ureg.watt


    @property
    def avg_vertical_oscillation(self):
        return self.avg_vertical_oscillation_mm*ureg.millimeter


    @property
    def avg_ground_contact_time(self):
        return self.avg_ground_contact_time_ms*ureg.milliseconds


    @property
    def avg_step_length(self):
        return self.avg_step_length_mm*ureg.millimeter


    @property
    def avg_power_density(self):
        return self.avg_power/self.avg_body_weight


    @property
    def avg_watts_per_kg(self):
        return self.avg_power_density.to('watt/kg').magnitude


    @property
    def country_to_percent_records_mapping(self):
        records = self.records
        num_records = len(records)
        mapping = {}
        for record in records:
            country_name = record.country_name
            mapping[country_name] = mapping.get(country_name, 0) + 1

        return {country_name: round(num/num_records*100, 2) for country_name, num in mapping.items()}


    @property
    def admin1_to_percent_records_mapping(self):
        records = self.records
        num_records = len(records)
        mapping = {}
        for record in records:
            admin1 = record.admin1
            mapping[admin1] = mapping.get(admin1, 0) + 1

        return {admin1: round(num/num_records*100, 2) for admin1, num in mapping.items()}


    @property
    def admin2_to_percent_records_mapping(self):
        records = self.records
        num_records = len(records)
        mapping = {}
        for record in records:
            admin2 = record.admin2
            mapping[admin2] = mapping.get(admin2, 0) + 1

        return {admin2: round(num/num_records*100, 2) for admin2, num in mapping.items()}


    @property
    def name_to_percent_records_mapping(self):
        records = self.records
        num_records = len(records)
        mapping = {}
        for record in records:
            name = record.name
            mapping[name] = mapping.get(name, 0) + 1

        return {name: round(num/num_records*100, 2) for name, num in mapping.items()}


class FitFilesToActivity:

    _activity_field_name_to_fit_file_field_name_mapping = {
        'start_time': 'start_time',
        'total_time_s': 'total_timer_time',
        'total_distance_m': 'total_distance',
        'calories_cal': 'total_calories',
        'avg_speed_m_s': 'avg_speed',
        'max_speed_m_s': 'max_speed',
        'total_ascent_m': 'total_ascent',
        'total_descent_m': 'total_descent',
        'avg_heart_rate_bpm': 'avg_heart_rate',
        'max_heart_rate_bpm': 'max_heart_rate',
        'aerobic_training_effect': 'total_training_effect',
        'anaerobic_training_effect': 'total_anaerobic_training_effect',
        'avg_temperature_c': 'avg_temperature',
        'max_temperature_c': 'max_temperature'
    }

    _running_activity_field_name_to_fit_file_session_value_name_mapping = {
        'avg_power_w': 'RP_AvgPower',
        'avg_cadence_steps_min': 'avg_running_cadence',
        'total_num_steps': 'total_strides',
        'avg_vertical_oscillation_mm': 'avg_vertical_oscillation',
        'avg_vertical_ratio': 'avg_vertical_ratio',
        'avg_ground_contact_time_ms': 'avg_stance_time',
        'avg_ground_contact_time_balance': 'avg_stance_time_balance',
        'avg_step_length_mm': 'avg_step_length'
    }

    _running_activity_field_name_to_fit_file_record_value_name_mapping = {
        'time': 'timestamp',
        'power_w': 'RP_Power',
        'altitude_m': 'altitude',
        'speed_m_s': 'speed',
        'vertical_oscillation_mm': 'vertical_oscillation',
        'vertical_ratio': 'vertical_ratio',
        'ground_contact_time_ms': 'stance_time',
        'ground_contact_time_balance': 'stance_time_balance',
        'heart_rate_bpm': 'heart_rate',
        'temperature_c': 'temperature',
        'step_length_mm': 'step_length',
        'cadence_steps_min': 'cadence'
    }

    _sport_to_modality_mapping = {'running': 'run', 'cycling': 'bike', 'walking': 'walking'}

    def __init__(self, *paths_to_fit_files):

        for path_to_fit_file in paths_to_fit_files:
            activity = self._fit_file_to_activity(path_to_fit_file)
            activity.save()


    @staticmethod
    def _convert_raw_lat_or_long_value_to_degrees(raw_value):
        return raw_value*180/2**31


    def _fit_file_to_activity(self, path_to_fit_file):

        fit_file = FitFile(path_to_fit_file)

        session_data = next(fit_file.get_messages(name='session'))

        start_location = Location(**self._get_start_location_data(session_data))
        start_location.save()

        records = fit_file.get_messages(name='record')

        device_data = next(fit_file.get_messages(name='device_info'))

        device = next(Device.objects.raw({'serial_number': f'{device_data.get_value("serial_number")}'}), None)

        if device is None:
            from IPython import embed; embed()
            raise TypeError

        sport = session_data.get_value('sport')

        if sport == 'running':
            records = self._convert_records(
                self._running_activity_field_name_to_fit_file_record_value_name_mapping,
                records,
                LocationWhileRunning,
                device
            )
            for record in records:
                record.save()
            return RunningActivity(
                source_file=open(path_to_fit_file, 'r+b'),
                start_location=start_location,
                device=device,
                records=records,
                **self._get_values_from_session_data(
                    {
                        **self._running_activity_field_name_to_fit_file_session_value_name_mapping,
                        **self._activity_field_name_to_fit_file_field_name_mapping
                    },
                    session_data
                )
            )


    @staticmethod
    def _get_values_from_session_data(activity_field_name_to_fit_file_session_value_name_mapping, session_data):
        return {
            activity_field_name: session_data.get_value(
                fit_file_session_value_name
            ) for activity_field_name, fit_file_session_value_name in activity_field_name_to_fit_file_session_value_name_mapping.items()
        }


    def _convert_records(self, record_field_name_to_fit_file_record_value_name_mapping, records, model_class, device):

        def baz(record):
            for record_field_name, fit_file_record_value_name in record_field_name_to_fit_file_record_value_name_mapping.items():
                try:
                    yield record_field_name, record.get_value(fit_file_record_value_name)
                except KeyError:
                    continue


        def foo():
            for record in records:

                try:
                    latitude = self._convert_raw_lat_or_long_value_to_degrees(record.get_value('position_lat'))
                    longitude = self._convert_raw_lat_or_long_value_to_degrees(record.get_value('position_long'))
                except KeyError:
                    continue

                converted_values = dict(baz(record))

                try:
                    converted_values['modality'] = self._sport_to_modality_mapping[record.get_value('activity_type')]
                except KeyError:
                    pass

                converted_values['device'] = device

                converted_values['latitude'] = latitude
                converted_values['longitude'] = longitude

                yield (latitude, longitude), converted_values

        converted_records = dict(foo())

        reverse_geocode_result = reverse_geocode_search(list(converted_records.keys()), verbose=False)

        def bar():
            for geocoded_location, converted_record in zip(reverse_geocode_result, converted_records.values()):

                converted_record['country_code'] = geocoded_location['cc']
                converted_record['admin1'] = geocoded_location['admin1']
                converted_record['admin2'] = geocoded_location['admin2']
                converted_record['name'] = geocoded_location['name']

                yield converted_record

        return [model_class(**converted_record) for converted_record in bar()]


    def _get_start_location_data(self, session_data):

        latitude = self._convert_raw_lat_or_long_value_to_degrees(session_data.get_value('start_position_lat'))
        longitude = self._convert_raw_lat_or_long_value_to_degrees(session_data.get_value('start_position_long'))

        reverse_geocode_result = reverse_geocode_search((latitude, longitude), verbose=False)
        reverse_geocode_result = reverse_geocode_result[0]

        return {
            'latitude': latitude,
            'longitude': longitude,
            'country_code': reverse_geocode_result['cc'],
            'admin1': reverse_geocode_result['admin1'],
            'admin2': reverse_geocode_result['admin2'],
            'name': reverse_geocode_result['name'],
            'time': session_data.get_value('start_time'),
            'modality': self._sport_to_modality_mapping[session_data.get_value('sport')]
        }
