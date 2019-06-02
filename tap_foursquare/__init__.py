#!/usr/bin/env python3
import json
import sys
import foursquare
import singer
from singer import metadata
from tap_foursquare.discover import discover_streams
from tap_foursquare.sync import sync_stream
from tap_foursquare.streams import STREAMS

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    "start_date"
]

# default authentication
OAUTH_CONFIG_KEYS = [
    "access_token"
]

def do_discover(client):
    LOGGER.info("Starting discover")
    catalog = {"streams": discover_streams(client)}
    json.dump(catalog, sys.stdout, indent=2)
    LOGGER.info("Finished discover")

def stream_is_selected(mdata):
    return mdata.get((), {}).get('selected', False)

def get_selected_streams(catalog):
    selected_stream_names = []
    for stream in catalog.streams:
        mdata = metadata.to_map(stream.metadata)
        if stream_is_selected(mdata):
            selected_stream_names.append(stream.tap_stream_id)
    return selected_stream_names

def populate_class_schemas(catalog, selected_stream_names):
    for stream in catalog.streams:
        if stream.tap_stream_id in selected_stream_names:
            STREAMS[stream.tap_stream_id].stream = stream

def do_sync(client, catalog, state, start_date):

    selected_stream_names = get_selected_streams(catalog)
    populate_class_schemas(catalog, selected_stream_names)

    for stream in catalog.streams:
        stream_name = stream.tap_stream_id
        mdata = metadata.to_map(stream.metadata)
        if stream_name not in selected_stream_names:
            LOGGER.info("%s: Skipping - not selected", stream_name)
            continue

        key_properties = metadata.get(mdata, (), 'table-key-properties')
        singer.write_schema(stream_name, stream.schema.to_dict(), key_properties)

        LOGGER.info("%s: Starting sync", stream_name)
        instance = STREAMS[stream_name](client)
        counter_value = sync_stream(state, start_date, instance)
        singer.write_state(state)
        LOGGER.info("%s: Completed sync (%s rows)", stream_name, counter_value)

    singer.write_state(state)
    LOGGER.info("Finished sync")

def oauth_auth(args):
    if not set(OAUTH_CONFIG_KEYS).issubset(args.config.keys()):
        LOGGER.debug("OAuth authentication unavailable.")
        return None

    creds = {
        "access_token": args.config['access_token']
    }

    client = foursquare.Foursquare(**creds)

    LOGGER.info("Using OAuth authentication.")
    return client

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    # OAuth has precedence
    client = oauth_auth(parsed_args)

    if not client:
        LOGGER.error("""No suitable authentication keys provided.""")

    if parsed_args.discover:
        do_discover(client)
    elif parsed_args.catalog:
        state = parsed_args.state
        do_sync(client, parsed_args.catalog, state, parsed_args.config['start_date'])
