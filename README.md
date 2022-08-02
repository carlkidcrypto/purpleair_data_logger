# purple_air_data_logger
 A logger that will query purple air sensor(s) for data. That data will then be ingested into a TimeScaleDB PostGreSQL database.

## Usage PurpleAirPSQLDataLogger.py 

```bash
usage: PurpleAirPSQLDataLogger.py [-h] -db_usr DB_USR [-db_host DB_HOST] -db DB [-db_port DB_PORT] [-db_pwd DB_PWD] -paa_read_key PAA_READ_KEY
                                  [-paa_sensor_index PAA_SENSOR_INDEX] [-paa_multiple_sensor_request_flag PAA_MULTIPLE_SENSOR_REQUEST_FLAG]
                                  [-paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE]

Collect data from PurpleAir sensors and insert into a database!

options:
  -h, --help            show this help message and exit
  -db_usr DB_USR        The PSQL database user
  -db_host DB_HOST      The PSQL database host
  -db DB                The PSQL database name
  -db_port DB_PORT      The PSQL database port number
  -db_pwd DB_PWD        The PSQL database password
  -paa_read_key PAA_READ_KEY
                        The PurpleAirAPI Read key
  -paa_sensor_index PAA_SENSOR_INDEX
                        The PurpleAirAPI sensor index for sending a single sensor request
  -paa_multiple_sensor_request_flag PAA_MULTIPLE_SENSOR_REQUEST_FLAG
                        This is a flag that by default is false. When set to true, we expect a json config file with parameters that will tell us how to
                        format our multiple sensor request.
  -paa_multiple_sensor_request_json_file PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE
                        If paa_multiple_sensor_request_flag is defined then this parameter is required. It shall be the path to a json file containing
                        the parameters to send a multiple sensor request.
```

### PAA_MULTIPLE_SENSOR_REQUEST_JSON_FILE Example

```json


```
