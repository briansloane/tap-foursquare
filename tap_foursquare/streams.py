import os
import json
import datetime
import pytz
import foursquare
import singer
from singer import metadata
from singer import utils
from singer.metrics import Point

LOGGER = singer.get_logger()
KEY_PROPERTIES = ['id']

def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

class Stream():
    name = None
    replication_method = None
    replication_key = None
    key_properties = KEY_PROPERTIES
    stream = None

    def __init__(self, client=None):
        self.client = client

    def get_bookmark(self, state):
        return utils.strptime_with_tz(singer.get_bookmark(state, self.name, self.replication_key))

    def update_bookmark(self, state, value):
        current_bookmark = self.get_bookmark(state)
        if value and utils.strptime_with_tz(value) > current_bookmark:
            singer.write_bookmark(state, self.name, self.replication_key, value)


    def load_schema(self):
        schema_file = "schemas/{}.json".format(self.name)
        with open(get_abs_path(schema_file)) as f:
            schema = json.load(f)
        return self._add_custom_fields(schema)

    def _add_custom_fields(self, schema): # pylint: disable=no-self-use
        return schema

    def load_metadata(self):
        schema = self.load_schema()
        mdata = metadata.new()

        mdata = metadata.write(mdata, (), 'table-key-properties', self.key_properties)
        mdata = metadata.write(mdata, (), 'forced-replication-method', self.replication_method)

        if self.replication_key:
            mdata = metadata.write(mdata, (), 'valid-replication-keys', [self.replication_key])

        for field_name in schema['properties'].keys():
            if field_name in self.key_properties or field_name == self.replication_key:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
            else:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')

        return metadata.to_list(mdata)

    def is_selected(self):
        return self.stream is not None

class Checkins(Stream):
    name = "checkins"
    replication_method = "INCREMENTAL"
    replication_key = "createdAt"

    def sync(self, state):
        bookmark = self.get_bookmark(state)
        checkins = self.client.users.checkins()

        for checkin in checkins['checkins']['items']:
            self.update_bookmark(state, datetime.datetime.fromtimestamp(checkin['createdAt']).strftime("%Y-%m-%dT%H:%M:%SZ"))
            yield (self.stream, checkin)

class Friends(Stream):
    name = "friends"
    replication_method = "FULL"

    def sync(self, state):
        friends = self.client.users.friends()
        for friend in friends['friends']['items']:
            yield (self.stream, friend)

STREAMS = {
    "checkins": Checkins,
    "friends": Friends
}
