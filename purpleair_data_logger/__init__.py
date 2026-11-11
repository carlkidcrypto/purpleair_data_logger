"""PurpleAir Data Logger: C++17 Telemetry Engine, SWIG Bindings, CLI & Cross-Platform GUIs."""

from __future__ import annotations

__version__ = "2026.11.3a0"

try:
    from .purpleair_data_logger_swig import (
        Batch,
        BatchVector,
        CliResult,
        CliRunner,
        CsvSinkConfig,
        DataLogger,
        DutConfig,
        DutConfigVector,
        GuiConfig,
        JsonlSinkConfig,
        LoggerConfig,
        LoggerStats,
        MetricConfig,
        MetricConfigVector,
        PrometheusSinkConfig,
        PsqlSinkConfig,
        Sample,
        SampleStatus_Error,
        SampleStatus_NoSuchInstance,
        SampleStatus_Ok,
        SampleStatus_Timeout,
        SampleVector,
        SinkRow,
        SinkRowVector,
        SinksConfig,
        SnmpConfig,
        SqliteSinkConfig,
        StringVector,
        TypeTag_Float64,
        TypeTag_Int64,
        TypeTag_Null,
        TypeTag_Str,
        ValidationReport,
        build_info,
        config_json_schema,
        generate_template_config_json,
        inspect_configured_sinks,
        is_valid_calsemver,
        purpleair_api_target_version,
        validate_config,
        validate_config_file,
        validate_config_json,
        version,
    )

    PurpleAirConfig = SnmpConfig
    SensorTargetConfig = DutConfig
    _HAS_NATIVE_SWIG = True
except ImportError:  # pragma: no cover
    _HAS_NATIVE_SWIG = False

    def version() -> str:
        return __version__

    def purpleair_api_target_version() -> str:
        return "2026.11.3"

    def build_info() -> str:
        return f"purpleair_data_logger {__version__} (pure-python fallback)"


def has_native_engine() -> bool:
    """Return True if the compiled C++17 SWIG extension is loaded."""
    return _HAS_NATIVE_SWIG


def has_purpleair_api_support() -> bool:
    """Return True if built with C++17 purpleair_api engine support."""
    return "purpleair_api=enabled" in build_info()


def has_sqlite3_support() -> bool:
    """Return True if built with SQLite3 sink support."""
    return "sqlite3=enabled" in build_info()


def has_embedded_sqlite3() -> bool:
    """Return True if built with embedded SQLite3 amalgamation."""
    return has_sqlite3_support()


def has_psql_support() -> bool:
    """Return True if built with libpq PostgreSQL/TimescaleDB support."""
    return "libpq=enabled" in build_info()


def supported_swig_languages() -> list[str]:
    """Return the 4 supported SWIG target languages."""
    return ["python", "javascript", "csharp", "go"]


__all__ = [
    "Batch",
    "BatchVector",
    "CliResult",
    "CliRunner",
    "CsvSinkConfig",
    "DataLogger",
    "DutConfig",
    "DutConfigVector",
    "GuiConfig",
    "JsonlSinkConfig",
    "LoggerConfig",
    "LoggerStats",
    "MetricConfig",
    "MetricConfigVector",
    "PrometheusSinkConfig",
    "PsqlSinkConfig",
    "PurpleAirConfig",
    "Sample",
    "SampleStatus_Error",
    "SampleStatus_NoSuchInstance",
    "SampleStatus_Ok",
    "SampleStatus_Timeout",
    "SampleVector",
    "SensorTargetConfig",
    "SinkRow",
    "SinkRowVector",
    "SinksConfig",
    "SnmpConfig",
    "SqliteSinkConfig",
    "StringVector",
    "TypeTag_Float64",
    "TypeTag_Int64",
    "TypeTag_Null",
    "TypeTag_Str",
    "ValidationReport",
    "__version__",
    "build_info",
    "config_json_schema",
    "generate_template_config_json",
    "has_embedded_sqlite3",
    "has_native_engine",
    "has_psql_support",
    "has_purpleair_api_support",
    "has_sqlite3_support",
    "inspect_configured_sinks",
    "is_valid_calsemver",
    "purpleair_api_target_version",
    "supported_swig_languages",
    "validate_config",
    "validate_config_file",
    "validate_config_json",
    "version",
]
