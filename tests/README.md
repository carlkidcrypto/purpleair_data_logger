# test

## Setup

1. Install python coverage

```bash
python3 -m pip install coverage
```

2. Install mock requests

```bash
python3 -m pip install requests-mock
```

3. Remove any currenlty installed versions of PurpleAirDataLogger

```bash
python3 -m pip uninstall purpleair_data_logger
```

## Running tests

```bash
python3 -m unittest && coverage html -d purpleair_data_logger_coverage_reports
```
