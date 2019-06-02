# tap-foursquare

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from the [Foursquare Places API](https://developer.foursquare.com/docs)
- Extracts the following resources:
  - [Checkins](https://developer.foursquare.com/docs/api/users/checkins)
  - [Friends](https://developer.foursquare.com/docs/api/users/friends)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

## Quick Start

1. Install

    ```bash
    pip install tap-foursquare
    ```

2. Create the config file

   Create a JSON file called `config.json`. Its contents should look like:

   ```json
    {
        "start_date": "2010-01-01",
        "access_token": "<Foursqure access_token>",
    }
    ```

   The `start_date` specifies the date at which the tap will begin pulling data
   (for those resources that support this).

4. Run the Tap in Discovery Mode

    ```bash
    tap-foursquare --config config.json --discover > catalog.json
    ```

   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode).

5. Run the Tap in Sync Mode

    ```bash
    tap-foursquare --config config.json --catalog catalog.json
    ```

---
