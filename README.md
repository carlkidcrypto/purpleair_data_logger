# Purple Air Data Logger(s) (PADLs)

A set of data logger(s) that will query purple air sensor(s) for data. That data will then be ingested into a TimeScaleDB PostGreSQL database, CSV files, or a SQLite3 database. To use these tools a PurpleAPI key is required. You can get API keys by sending an email to `contact@purpleair.com` with a first and last name to assign them to.

| [![Behave Tests](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/behave_tests.yml/badge.svg?branch=main)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/behave_tests.yml) | [![PyPI Distributions](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/build_and_publish_to_pypi.yml/badge.svg?branch=main)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/build_and_publish_to_pypi.yml) | [![TestPyPI Distributions](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/build_and_publish_to_test_pypi.yml/badge.svg?branch=main)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/build_and_publish_to_test_pypi.yml) | [![Black](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/black.yml/badge.svg)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/black.yml) |
| --------------- | --------------- | --------------- | --------------- |

| [![Pull Request Sphinx Docs Check](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/sphinx_build.yml/badge.svg)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/sphinx_build.yml) | [![pages-build-deployment](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/pages/pages-build-deployment) | [![CodeQL](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/carlkidcrypto/purpleair_data_logger/actions/workflows/github-code-scanning/codeql) | |
| --------------- | --------------- | --------------- | --------------- |

## How to Support This Project

<a href="https://www.buymeacoffee.com/carlkidcrypto" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

## Installation

You can install the PurpleAir Data Logger via pip.

```bash
python3 -m pip install purpleair_data_logger
```

You can install PurpleAir Data Logger by cloning down this repo.

```bash
git clone https://github.com/carlkidcrypto/purpleair_data_logger.git
cd purpleair_data_logger
python3 -m pip install .
```

## Usage PurpleAirPSQLDataLogger.py

```bash
usage: PurpleAirPSQLDataLogger.py [-h] [-paa_read_key PAA_READ_KEY] [-paa_write_key PAA_WRITE_KEY] [-paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE]
                                  [-paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE] [-paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE]
                                  [-paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE] [-db_drop_all_tables] -db_usr DB_USR [-db_host DB_HOST] -db DB [-db_port DB_PORT]
                                  [-db_pwd DB_PWD]

Collect data from PurpleAir sensors and insert into a database!

optional arguments:
  -h, --help            show this help message and exit
  -paa_read_key PAA_READ_KEY
                        The PurpleAirAPI Read key
  -paa_write_key PAA_WRITE_KEY
                        The PurpleAirAPI write key
  -paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a single sensor request.
  -paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a multiple sensor request.
  -paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a group sensor request.
  -paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a local sensor request.
  -db_drop_all_tables   Set this flag if you wish to drop all tables before loading in new data. Useful if a database change has happened. Note: Make sure to provide a db_usr with DROP rights.
                        WARNING: ALL COLLECTED DATA WILL BE LOST!
  -db_usr DB_USR        The PSQL database user
  -db_host DB_HOST      The PSQL database host
  -db DB                The PSQL database name
  -db_port DB_PORT      The PSQL database port number
  -db_pwd DB_PWD        The PSQL database password
```

Using it with single sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirPSQLDataLogger -db_usr USER -db_host localhost -db DB_NAME -db_port 5432 -db_pwd PASSWORD -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_single_sensor_request_json_file PATH_TO_YOUR_FILE
```

Using it with multiple sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirPSQLDataLogger -db_usr USER -db_host localhost -db DB_NAME -db_port 5432 -db_pwd PASSWORD -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_multiple_sensor_request_json_file PATH_TO_YOUR_FILE
```

### High Level Design

![PAA_Data_Logger_Software_Stack.drawio.png](/diagrams/PAA_Data_Logger_Software_Stack.drawio.png)

### Getting Started

1. Grab and install Postgresql for your platform. <https://www.postgresql.org/download/>
2. Create two database users. One for Grafana with select only privileges. The other for the data logger with only insert/create privileges. <https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e>, <https://www.techonthenet.com/postgresql/grant_revoke.php>
3. Install and configure TimescaleDB. <https://docs.timescale.com/install/latest/self-hosted/>
4. Install and configure Grafana. <https://grafana.com/docs/grafana/latest/setup-grafana/installation/>
5. Import into your local Grafana instance the dashboard file found [here](./grafana_dashboards/PurpleAirAPI%20(PAA)%20Data%20Logger%20Grafana%20Dashboard-1660355898051.json)

## Usage PurpleAirCSVDataLogger.py

```bash
usage: PurpleAirCSVDataLogger.py [-h] [-paa_read_key PAA_READ_KEY] [-paa_write_key PAA_WRITE_KEY] [-paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE]
                                 [-paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE] [-paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE]
                                 [-paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE] -save_file_path SAVE_FILE_PATH

Collect data from PurpleAir sensors and store it in CSV files!

optional arguments:
  -h, --help            show this help message and exit
  -paa_read_key PAA_READ_KEY
                        The PurpleAirAPI Read key
  -paa_write_key PAA_WRITE_KEY
                        The PurpleAirAPI write key
  -paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a single sensor request.
  -paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a multiple sensor request.
  -paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a group sensor request.
  -paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a local sensor request.
  -save_file_path SAVE_FILE_PATH
                        The path to save CSV files in.
```

Using it with single sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirCSVDataLogger -save_file_path SAVE_FILE_PATH -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_single_sensor_request_json_file PATH_TO_YOUR_FILE
```

Using it with multiple sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirCSVDataLogger -save_file_path SAVE_FILE_PATH -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_multiple_sensor_request_json_file PATH_TO_YOUR_FILE
```

## Usage PurpleAirSQLiteDataLogger.py

```bash
usage: PurpleAirSQLiteDataLogger.py [-h] [-paa_read_key PAA_READ_KEY] [-paa_write_key PAA_WRITE_KEY] [-paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE]
                                    [-paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE] [-paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE]
                                    [-paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE] -db_name DB_NAME

Collect data from PurpleAir sensors and store it a SQLite3 database file!

optional arguments:
  -h, --help            show this help message and exit
  -paa_read_key PAA_READ_KEY
                        The PurpleAirAPI Read key
  -paa_write_key PAA_WRITE_KEY
                        The PurpleAirAPI write key
  -paa_single_sensor_request_json_file PAA_SINGLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a single sensor request.
  -paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a multiple sensor request.
  -paa_group_sensor_request_json_file PAA_GROUP_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a group sensor request.
  -paa_local_sensor_request_json_file PAA_LOCAL_SENSOR_REQUEST_JSON_FILE
                        The path to a json file containing the parameters to send a local sensor request.
  -db_name DB_NAME      The path and name for the SQLite3 database file! i.e database_name.db
```

Using it with single sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirSQLiteDataLogger -db_name DB_NAME -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_single_sensor_request_json_file PATH_TO_YOUR_FILE
```

Using it with multiple sensor requests...

```bash
python3 -m  purpleair_data_logger.PurpleAirSQLiteDataLogger -db_name DB_NAME -paa_read_key 12345678-1234-1234-1234-123456789123 -paa_write_key 12345678-1234-1234-1234-123456789123 -paa_multiple_sensor_request_json_file PATH_TO_YOUR_FILE
```

## Sample JSON Configuration File(s)

The following sample json configuration files can be used with any of the data loggers.

### PAA Single Sensor Request Example

Out of the parameters in the file below "sensor_index" is required. The others are all optional according to PurpleAirAPI (PAA) documentation. If a field is not being used, mark it 'null' without the single quotes.

See this [file](./sample_json_config_files/sample_single_sensor_request_json_file.json) for an example.

> Note: `poll_interval_seconds` is also required. It can not be lower than `60`. This is a custom field not defined by the PAA documentation.
> Note: Refer to the PurpleAirAPI (PAA) documentation for more information. <https://api.purpleair.com/#api-sensors-get-sensor-data>

### PAA Multiple Sensor Request Example

Out of the parameters in the file below "fields" is required. The others are all optional according to PurpleAirAPI (PAA) documentation. If a field is not being used, mark it 'null' without the single quotes.

See this [file](./sample_json_config_files/sample_multiple_sensor_request_json_file.json) for an example.

> Note: `poll_interval_seconds` is also required. It can not be lower than `60`. This is a custom field not defined by the PAA documentation.
> Note: Refer to the PurpleAirAPI (PAA) documentation for more information. <https://api.purpleair.com/#api-sensors-get-sensors-data>

The below snippet is taken From the PurpleAirAPI (PAA) documentation:

```plain text
  Field Type Description
  fields String
  The 'Fields' parameter specifies which 'sensor data fields' to include in the response. It is a comma separated list with one or more of the following:

  Station information and status fields:
  name, icon, model, hardware, location_type, private, latitude, longitude, altitude, position_rating, led_brightness, firmware_version, firmware_upgrade, rssi, uptime, pa_latency, memory, last_seen, last_modified, date_created, channel_state, channel_flags, channel_flags_manual, channel_flags_auto, confidence, confidence_manual, confidence_auto

  Environmental fields:
  humidity, humidity_a, humidity_b, temperature, temperature_a, temperature_b, pressure, pressure_a, pressure_b

  Miscellaneous fields:
  voc, voc_a, voc_b, ozone1, analog_input

  PM1.0 fields:
  pm1.0, pm1.0_a, pm1.0_b, pm1.0_atm, pm1.0_atm_a, pm1.0_atm_b, pm1.0_cf_1, pm1.0_cf_1_a, pm1.0_cf_1_b

  PM2.5 fields:
  pm2.5_alt, pm2.5_alt_a, pm2.5_alt_b, pm2.5, pm2.5_a, pm2.5_b, pm2.5_atm, pm2.5_atm_a, pm2.5_atm_b, pm2.5_cf_1, pm2.5_cf_1_a, pm2.5_cf_1_b

  PM2.5 pseudo (simple running) average fields:
  pm2.5_10minute, pm2.5_10minute_a, pm2.5_10minute_b, pm2.5_30minute, pm2.5_30minute_a, pm2.5_30minute_b, pm2.5_60minute, pm2.5_60minute_a, pm2.5_60minute_b, pm2.5_6hour, pm2.5_6hour_a, pm2.5_6hour_b, pm2.5_24hour, pm2.5_24hour_a, pm2.5_24hour_b, pm2.5_1week, pm2.5_1week_a, pm2.5_1week_b

  PM10.0 fields:
  pm10.0, pm10.0_a, pm10.0_b, pm10.0_atm, pm10.0_atm_a, pm10.0_atm_b, pm10.0_cf_1, pm10.0_cf_1_a, pm10.0_cf_1_b

  Visibility fields:
  scattering_coefficient, scattering_coefficient_a, scattering_coefficient_b, deciviews, deciviews_a, deciviews_b, visual_range, visual_range_a, visual_range_b

  Particle count fields:
  0.3_um_count, 0.3_um_count_a, 0.3_um_count_b, 0.5_um_count, 0.5_um_count_a, 0.5_um_count_b, 1.0_um_count, 1.0_um_count_a, 1.0_um_count_b, 2.5_um_count, 2.5_um_count_a, 2.5_um_count_b, 5.0_um_count, 5.0_um_count_a, 5.0_um_count_b, 10.0_um_count 10.0_um_count_a, 10.0_um_count_b

  ThingSpeak fields, used to retrieve data from api.thingspeak.com:
  primary_id_a, primary_key_a, secondary_id_a, secondary_key_a, primary_id_b, primary_key_b, secondary_id_b, secondary_key_b

  For field descriptions, please see the 'sensor data fields'. section.

  location_type optional Number
  The location_type of the sensors.
  Possible values are: 0 = Outside or 1 = Inside.

  read_keys optional String
  A read_key is required for private devices. It is separate to the api_key and each sensor has its own read_key. Submit multiple keys by separating them with a comma (,) character for example: key-one,key-two,key-three.

  show_only optional String
  A comma (,) separated list of sensor_index values. When provided, the results are limited only to the sensors included in this list.

  modified_since optional long
  The modified_since parameter causes only sensors modified after the provided time stamp to be included in the results. Using the time_stamp value from a previous call (recommended) will limit results to those with new values since the last request. Using a value of 0 will match sensors modified at any time.

  max_age optional Integer
  Filter results to only include sensors modified or updated within the last number of seconds. Using a value of 0 will match sensors of any age.

  Default value: 604800

  nwlng optional Number
  A north west longitude for the bounding box.

  Use a bounding box to limit the sensors returned to a specific geographic area. The bounding box is defined by two points, a north west latitude/longitude and a south east latitude/longitude.

  nwlat optional Number
  A north west latitude for the bounding box.

  selng optional Number
  A south east longitude for the bounding box.

  selat optional Number
  A south east latitude for the bounding box.
```

### PAA Group Sensor Request Example

Out of the parameters in the file below `sensor_group_name`, `add_sensors_to_group`, and `sensor_index_list` are custom settings not
defined in the official PAA documentation. These three setting help drive the `group` request feature.

`sensor_group_name` - This will be the name assigned to your group. If it doesn't exist already, it will be created.
Otherwise, the first group matching the name will be used.

`add_sensors_to_group` - If true, adds the sensors in the `sensor_index_list`. If false, `sensor_index_list` is ignored.

`sensor_index_list` -  A list of sensor indexes that will be added to your group if they don't already exist.

The rest of the settings are official PAA settings. They are the same as the [### PAA Multiple Sensor Request Example](#paa-multiple-sensor-request-example). Refer above for details.

> Note: `poll_interval_seconds` is also required. It can not be lower than `60`. This is a custom field not defined by the PAA documentation.

See this [file](./sample_json_config_files/sample_group_sensor_request_json_file.json) for an example.

### PAA Local Sensor Request Example

Out of the parameters in the file below all are custom settings and are required.

`sensor_ip_list` - A string list of IPv4 addresses with no CIDR.

`poll_interval_seconds` - The poll interval to get information from local sensors on the network.

See this [file](./sample_json_config_files/sample_local_sensor_request_json_file.json) for an example.
