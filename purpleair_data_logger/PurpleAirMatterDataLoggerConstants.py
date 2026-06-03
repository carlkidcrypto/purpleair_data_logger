#!/usr/bin/env python3
"""
Copyright 2025 carlkidcrypto, All rights reserved.

Matter Data Logger constants for PurpleAir sensors.

Maps PurpleAir sensor fields to Matter device type structures per the
Connectivity Standards Alliance Matter 1.5.1 Specification.

Requires: purpleair_api >= 1.5.0a1 (includes purpleair_api.matter)
"""

# =============================================================================
# HTTP Server
# =============================================================================

#: Default HTTP server port for the Matter data logger web interface.
MATTER_DATA_LOGGER_DEFAULT_PORT = 9855
#: Default host to bind the HTTP server to (use 127.0.0.1 to avoid exposing the API by default).
MATTER_DATA_LOGGER_DEFAULT_HOST = "127.0.0.1"

# =============================================================================
# API Routes
# =============================================================================

#: Path for the all-sensors Matter device list endpoint.
MATTER_ALL_SENSORS_PATH = "/matter/sensors"

#: Path prefix for individual sensor Matter device endpoint.
MATTER_SENSOR_PATH_PREFIX = "/matter/sensor"

#: Path for the health check endpoint.
HEALTH_PATH = "/health"

# =============================================================================
# Prometheus-compatible metric labels (for scraping the HTTP server itself)
# =============================================================================

#: Metric name for data_timestamp
STATION_DATA_TIME_STAMP_METRIC_NAME = "purpleair_matter_data_timestamp"
STATION_DATA_TIME_STAMP_METRIC_DESCRIPTION = (
    "PurpleAir Matter data timestamp (Unix epoch seconds)"
)

#: Metric name for sensor_count
STATION_SENSOR_COUNT_METRIC_NAME = "purpleair_matter_sensor_count"
STATION_SENSOR_COUNT_METRIC_DESCRIPTION = (
    "Number of PurpleAir sensors converted to Matter device format"
)

# =============================================================================
# Logging
# =============================================================================

#: Default log level for the Matter data logger.
MATTER_DATA_LOGGER_LOG_LEVEL = "INFO"