#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "purpleair_data_logger/datatypes.h"

namespace purpleair_data_logger {

struct MetricConfig {
   std::string name;
   std::string oid;
   std::string operation = "get"; // "get", "getnext", "walk", "bulkget", "bulkwalk", "single",
                                  // "multiple", "history", "local"
   int max_repeaters = 25;
};

struct SnmpConfig {
   std::string mode = "stub";  // "stub", "purpleair", "cloud_single", "cloud_multiple",
                               // "cloud_group", "local", or "ezsnmp"
   std::string version = "2c"; // "1", "2c", "3"
   std::string community = "public";
   int port = 80;
   int retries = 3;
   int timeout_sec = 10;

   // PurpleAir API parameters
   std::string api_read_key;
   std::string api_write_key;
   int sensor_index = 53;
   std::string read_key;
   int group_id = 0;
   std::string ipv4_address;
   std::string location_type;
   std::string show_only;
   int max_age = 0;
   std::string fields =
       "name,pm2.5_atm,pm2.5_cf_1,pm1.0_atm,pm10.0_atm,temperature,humidity,pressure,voc,rssi,"
       "uptime";

   // Auth parameters (retained for schema compatibility)
   std::string security_level = "noAuthNoPriv";
   std::string security_username;
   std::string auth_protocol = "SHA";
   std::string auth_passphrase;
   std::string priv_protocol = "AES";
   std::string priv_passphrase;
   std::string context_name;
   std::string context_engine_id;
   std::string security_engine_id;
};

using PurpleAirConfig = SnmpConfig;

struct DutConfig {
   std::string name;
   std::string dut_ip;
   bool enabled = true;
   int poll_interval_ms = 60000;
   SnmpConfig snmp;
   std::vector<MetricConfig> metrics;
};

using SensorTargetConfig = DutConfig;

struct SqliteSinkConfig {
   bool enabled = true;
   std::string path = "data/purpleair_telemetry.sqlite";
   bool wal_mode = true;
   int busy_timeout_ms = 5000;
   int commit_batch_size = 500;
   int commit_interval_ms = 1000;
};

struct CsvSinkConfig {
   bool enabled = false;
   std::string directory = "data/csv";
   int flush_every_n_batches = 1;
};

struct JsonlSinkConfig {
   bool enabled = false;
   std::string directory = "data/jsonl";
   int flush_every_n_batches = 1;
};

struct PsqlSinkConfig {
   bool enabled = false;
   std::string conninfo = "host=localhost port=5432 dbname=purpleair user=postgres";
   std::string schema = "public";
   bool use_timescaledb = false;
   int commit_batch_size = 500;
};

struct PrometheusSinkConfig {
   bool enabled = false;
   std::string bind_host = "127.0.0.1";
   int port = 9760;
   std::string metric_prefix = "purpleair";
};

struct SinksConfig {
   SqliteSinkConfig sqlite;
   CsvSinkConfig csv;
   JsonlSinkConfig jsonl;
   PsqlSinkConfig psql;
   PrometheusSinkConfig prometheus;
};

struct GuiConfig {
   std::string frontend = "auto"; // "auto", "tk", "web"
   std::string web_host = "127.0.0.1";
   int web_port = 8765;
   bool open_browser = true;
   int refresh_interval_ms = 1000;
   std::string theme = "dark";
   std::string locale = "en";
   std::string locale_file;
};

struct LoggerConfig {
   std::string instance_name = "purpleair_data_logger";
   std::string log_level = "INFO";
   size_t queue_capacity = 4096;
   int max_poll_Cycles = 0; // 0 = run until stopped
   std::vector<DutConfig> duts;
   SinksConfig sinks;
   GuiConfig gui;

   static LoggerConfig from_json_string(std::string const& json_str);
   static LoggerConfig from_json_file(std::string const& path);

   std::string to_json_string(int indent = 2) const;
   void save_json_file(std::string const& path, int indent = 2) const;
};

ValidationReport validate_config(LoggerConfig const& cfg);
ValidationReport validate_config_json(std::string const& json_str);
ValidationReport validate_config_file(std::string const& path);

std::string generate_template_config_json(std::string const& profile = "minimal");
std::string config_json_schema();

} // namespace purpleair_data_logger
