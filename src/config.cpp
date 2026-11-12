#include "purpleair_data_logger/config.h"

#include <filesystem>
#include <fstream>
#include <sstream>
#include <unordered_set>

#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"

namespace purpleair_data_logger {

namespace {
std::string read_file_text(std::string const& path) {
   std::ifstream ifs(path, std::ios::in | std::ios::binary);
   if (!ifs) {
      throw ConfigError("Unable to open configuration file: " + path);
   }
   std::ostringstream oss;
   oss << ifs.rdbuf();
   return oss.str();
}
} // namespace

LoggerConfig LoggerConfig::from_json_string(std::string const& json_str) {
   json::Value root = json::Value::parse(json_str);
   if (!root.is_object()) {
      throw ConfigError("Configuration root must be a JSON object");
   }

   LoggerConfig cfg;
   json::Value const& logger_obj = root.contains("logger") ? root.get("logger") : root;
   if (logger_obj.is_object()) {
      cfg.instance_name = logger_obj.get("instance_name").as_string(cfg.instance_name);
      cfg.log_level = logger_obj.get("log_level").as_string(cfg.log_level);
      cfg.queue_capacity = static_cast<size_t>(
          logger_obj.get("queue_capacity").as_int64(static_cast<int64_t>(cfg.queue_capacity)));
      cfg.max_poll_Cycles = logger_obj.get("max_poll_cycles").as_int(cfg.max_poll_Cycles);
   }

   json::Value const& duts_arr = root.contains("duts") ? root.get("duts") : root.get("sensors");
   if (duts_arr.is_array()) {
      for (auto const& dval : duts_arr.as_array()) {
         if (!dval.is_object()) {
            continue;
         }
         DutConfig dut;
         dut.name = dval.get("name").as_string();
         dut.dut_ip = dval.get("dut_ip").as_string(dval.get("host").as_string("api.purpleair.com"));
         dut.enabled = dval.get("enabled").as_bool(true);
         dut.poll_interval_ms = dval.get("poll_interval_ms").as_int(60000);

         json::Value const& snmp_obj =
             dval.contains("purpleair") ? dval.get("purpleair") : dval.get("snmp");
         if (snmp_obj.is_object()) {
            dut.snmp.mode = snmp_obj.get("mode").as_string(dut.snmp.mode);
            dut.snmp.version = snmp_obj.get("version").as_string(dut.snmp.version);
            dut.snmp.community = snmp_obj.get("community").as_string(dut.snmp.community);
            dut.snmp.port = snmp_obj.get("port").as_int(dut.snmp.port);
            dut.snmp.retries = snmp_obj.get("retries").as_int(dut.snmp.retries);
            dut.snmp.timeout_sec = snmp_obj.get("timeout_sec").as_int(dut.snmp.timeout_sec);
            dut.snmp.api_read_key = snmp_obj.get("api_read_key").as_string(dut.snmp.api_read_key);
            dut.snmp.api_write_key =
                snmp_obj.get("api_write_key").as_string(dut.snmp.api_write_key);
            dut.snmp.sensor_index = snmp_obj.get("sensor_index").as_int(dut.snmp.sensor_index);
            dut.snmp.read_key = snmp_obj.get("read_key").as_string(dut.snmp.read_key);
            dut.snmp.group_id = snmp_obj.get("group_id").as_int(dut.snmp.group_id);
            dut.snmp.ipv4_address = snmp_obj.get("ipv4_address").as_string(dut.snmp.ipv4_address);
            dut.snmp.location_type =
                snmp_obj.get("location_type").as_string(dut.snmp.location_type);
            dut.snmp.show_only = snmp_obj.get("show_only").as_string(dut.snmp.show_only);
            dut.snmp.max_age = snmp_obj.get("max_age").as_int(dut.snmp.max_age);
            dut.snmp.fields = snmp_obj.get("fields").as_string(dut.snmp.fields);
            dut.snmp.security_level =
                snmp_obj.get("security_level").as_string(dut.snmp.security_level);
            dut.snmp.security_username =
                snmp_obj.get("security_username").as_string(dut.snmp.security_username);
            dut.snmp.auth_protocol =
                snmp_obj.get("auth_protocol").as_string(dut.snmp.auth_protocol);
            dut.snmp.auth_passphrase =
                snmp_obj.get("auth_passphrase").as_string(dut.snmp.auth_passphrase);
            dut.snmp.priv_protocol =
                snmp_obj.get("priv_protocol").as_string(dut.snmp.priv_protocol);
            dut.snmp.priv_passphrase =
                snmp_obj.get("priv_passphrase").as_string(dut.snmp.priv_passphrase);
            dut.snmp.context_name = snmp_obj.get("context_name").as_string(dut.snmp.context_name);
            dut.snmp.context_engine_id =
                snmp_obj.get("context_engine_id").as_string(dut.snmp.context_engine_id);
            dut.snmp.security_engine_id =
                snmp_obj.get("security_engine_id").as_string(dut.snmp.security_engine_id);
         }

         json::Value const& metrics_arr = dval.get("metrics");
         if (metrics_arr.is_array()) {
            for (auto const& mval : metrics_arr.as_array()) {
               if (!mval.is_object()) {
                  continue;
               }
               MetricConfig m;
               m.name = mval.get("name").as_string();
               m.oid = mval.get("oid").as_string(mval.get("field").as_string(m.name));
               m.operation = mval.get("operation").as_string("get");
               m.max_repeaters = mval.get("max_repeaters").as_int(25);
               dut.metrics.push_back(std::move(m));
            }
         }
         cfg.duts.push_back(std::move(dut));
      }
   }

   json::Value const& sinks_obj = root.get("sinks");
   if (sinks_obj.is_object()) {
      json::Value const& sq = sinks_obj.get("sqlite");
      if (sq.is_object()) {
         cfg.sinks.sqlite.enabled = sq.get("enabled").as_bool(cfg.sinks.sqlite.enabled);
         cfg.sinks.sqlite.path = sq.get("path").as_string(cfg.sinks.sqlite.path);
         cfg.sinks.sqlite.wal_mode = sq.get("wal_mode").as_bool(cfg.sinks.sqlite.wal_mode);
         cfg.sinks.sqlite.busy_timeout_ms =
             sq.get("busy_timeout_ms").as_int(cfg.sinks.sqlite.busy_timeout_ms);
         cfg.sinks.sqlite.commit_batch_size =
             sq.get("commit_batch_size").as_int(cfg.sinks.sqlite.commit_batch_size);
         cfg.sinks.sqlite.commit_interval_ms =
             sq.get("commit_interval_ms").as_int(cfg.sinks.sqlite.commit_interval_ms);
      }
      json::Value const& csv = sinks_obj.get("csv");
      if (csv.is_object()) {
         cfg.sinks.csv.enabled = csv.get("enabled").as_bool(cfg.sinks.csv.enabled);
         cfg.sinks.csv.directory = csv.get("directory").as_string(cfg.sinks.csv.directory);
         cfg.sinks.csv.flush_every_n_batches =
             csv.get("flush_every_n_batches").as_int(cfg.sinks.csv.flush_every_n_batches);
      }
      json::Value const& jl = sinks_obj.get("jsonl");
      if (jl.is_object()) {
         cfg.sinks.jsonl.enabled = jl.get("enabled").as_bool(cfg.sinks.jsonl.enabled);
         cfg.sinks.jsonl.directory = jl.get("directory").as_string(cfg.sinks.jsonl.directory);
         cfg.sinks.jsonl.flush_every_n_batches =
             jl.get("flush_every_n_batches").as_int(cfg.sinks.jsonl.flush_every_n_batches);
      }
      json::Value const& pg = sinks_obj.get("psql");
      if (pg.is_object()) {
         cfg.sinks.psql.enabled = pg.get("enabled").as_bool(cfg.sinks.psql.enabled);
         cfg.sinks.psql.conninfo = pg.get("conninfo").as_string(cfg.sinks.psql.conninfo);
         cfg.sinks.psql.schema = pg.get("schema").as_string(cfg.sinks.psql.schema);
         cfg.sinks.psql.use_timescaledb =
             pg.get("use_timescaledb").as_bool(cfg.sinks.psql.use_timescaledb);
         cfg.sinks.psql.commit_batch_size =
             pg.get("commit_batch_size").as_int(cfg.sinks.psql.commit_batch_size);
      }
      json::Value const& pr = sinks_obj.get("prometheus");
      if (pr.is_object()) {
         cfg.sinks.prometheus.enabled = pr.get("enabled").as_bool(cfg.sinks.prometheus.enabled);
         cfg.sinks.prometheus.bind_host =
             pr.get("bind_host").as_string(cfg.sinks.prometheus.bind_host);
         cfg.sinks.prometheus.port = pr.get("port").as_int(cfg.sinks.prometheus.port);
         cfg.sinks.prometheus.metric_prefix =
             pr.get("metric_prefix").as_string(cfg.sinks.prometheus.metric_prefix);
      }
   } else if (sinks_obj.is_array()) {
      cfg.sinks.sqlite.enabled = false;
      cfg.sinks.csv.enabled = false;
      cfg.sinks.jsonl.enabled = false;
      cfg.sinks.psql.enabled = false;
      cfg.sinks.prometheus.enabled = false;
      for (auto const& item : sinks_obj.as_array()) {
         if (!item.is_object()) {
            continue;
         }
         std::string stype = item.get("type").as_string();
         bool en = item.get("enabled").as_bool(true);
         if (stype == "sqlite3" || stype == "sqlite") {
            cfg.sinks.sqlite.enabled = en;
            cfg.sinks.sqlite.path = item.get("path").as_string(cfg.sinks.sqlite.path);
         } else if (stype == "csv") {
            cfg.sinks.csv.enabled = en;
            cfg.sinks.csv.directory =
                item.get("directory").as_string(item.get("dir").as_string(cfg.sinks.csv.directory));
         } else if (stype == "jsonl") {
            cfg.sinks.jsonl.enabled = en;
            cfg.sinks.jsonl.directory =
                item.get("directory")
                    .as_string(item.get("dir").as_string(cfg.sinks.jsonl.directory));
         } else if (stype == "psql") {
            cfg.sinks.psql.enabled = en;
            cfg.sinks.psql.conninfo = item.get("conninfo").as_string(cfg.sinks.psql.conninfo);
         } else if (stype == "prometheus") {
            cfg.sinks.prometheus.enabled = en;
            cfg.sinks.prometheus.port = item.get("port").as_int(cfg.sinks.prometheus.port);
         }
      }
   }

   json::Value const& gui_obj = root.get("gui");
   if (gui_obj.is_object()) {
      cfg.gui.frontend = gui_obj.get("frontend").as_string(cfg.gui.frontend);
      cfg.gui.web_host = gui_obj.get("web_host").as_string(cfg.gui.web_host);
      cfg.gui.web_port = gui_obj.get("web_port").as_int(cfg.gui.web_port);
      cfg.gui.open_browser = gui_obj.get("open_browser").as_bool(cfg.gui.open_browser);
      cfg.gui.refresh_interval_ms =
          gui_obj.get("refresh_interval_ms").as_int(cfg.gui.refresh_interval_ms);
      cfg.gui.theme = gui_obj.get("theme").as_string(cfg.gui.theme);
      cfg.gui.locale = gui_obj.get("locale").as_string(cfg.gui.locale);
      cfg.gui.locale_file = gui_obj.get("locale_file").as_string(cfg.gui.locale_file);
   }

   return cfg;
}

LoggerConfig LoggerConfig::from_json_file(std::string const& path) {
   return from_json_string(read_file_text(path));
}

std::string LoggerConfig::to_json_string(int indent) const {
   json::Value root = json::Value::make_object();

   json::Value logger_obj = json::Value::make_object();
   logger_obj.set("instance_name", json::Value(instance_name));
   logger_obj.set("log_level", json::Value(log_level));
   logger_obj.set("queue_capacity", json::Value(static_cast<int64_t>(queue_capacity)));
   logger_obj.set("max_poll_cycles", json::Value(max_poll_Cycles));
   root.set("logger", std::move(logger_obj));

   json::Value duts_arr = json::Value::make_array();
   for (auto const& d : duts) {
      json::Value dobj = json::Value::make_object();
      dobj.set("name", json::Value(d.name));
      dobj.set("dut_ip", json::Value(d.dut_ip));
      dobj.set("enabled", json::Value(d.enabled));
      dobj.set("poll_interval_ms", json::Value(d.poll_interval_ms));

      json::Value snmp_obj = json::Value::make_object();
      snmp_obj.set("mode", json::Value(d.snmp.mode));
      snmp_obj.set("version", json::Value(d.snmp.version));
      snmp_obj.set("community", json::Value(d.snmp.community));
      snmp_obj.set("port", json::Value(d.snmp.port));
      snmp_obj.set("retries", json::Value(d.snmp.retries));
      snmp_obj.set("timeout_sec", json::Value(d.snmp.timeout_sec));
      snmp_obj.set("api_read_key", json::Value(d.snmp.api_read_key));
      snmp_obj.set("api_write_key", json::Value(d.snmp.api_write_key));
      snmp_obj.set("sensor_index", json::Value(d.snmp.sensor_index));
      snmp_obj.set("read_key", json::Value(d.snmp.read_key));
      snmp_obj.set("group_id", json::Value(d.snmp.group_id));
      snmp_obj.set("ipv4_address", json::Value(d.snmp.ipv4_address));
      snmp_obj.set("location_type", json::Value(d.snmp.location_type));
      snmp_obj.set("show_only", json::Value(d.snmp.show_only));
      snmp_obj.set("max_age", json::Value(d.snmp.max_age));
      snmp_obj.set("fields", json::Value(d.snmp.fields));
      snmp_obj.set("security_level", json::Value(d.snmp.security_level));
      snmp_obj.set("security_username", json::Value(d.snmp.security_username));
      snmp_obj.set("auth_protocol", json::Value(d.snmp.auth_protocol));
      snmp_obj.set("auth_passphrase", json::Value(d.snmp.auth_passphrase));
      snmp_obj.set("priv_protocol", json::Value(d.snmp.priv_protocol));
      snmp_obj.set("priv_passphrase", json::Value(d.snmp.priv_passphrase));
      snmp_obj.set("context_name", json::Value(d.snmp.context_name));
      snmp_obj.set("context_engine_id", json::Value(d.snmp.context_engine_id));
      snmp_obj.set("security_engine_id", json::Value(d.snmp.security_engine_id));
      dobj.set("snmp", std::move(snmp_obj));

      json::Value marr = json::Value::make_array();
      for (auto const& m : d.metrics) {
         json::Value mobj = json::Value::make_object();
         mobj.set("name", json::Value(m.name));
         mobj.set("oid", json::Value(m.oid));
         mobj.set("operation", json::Value(m.operation));
         mobj.set("max_repeaters", json::Value(m.max_repeaters));
         marr.push_back(std::move(mobj));
      }
      dobj.set("metrics", std::move(marr));
      duts_arr.push_back(std::move(dobj));
   }
   root.set("duts", std::move(duts_arr));

   json::Value sinks_obj = json::Value::make_object();
   {
      json::Value sq = json::Value::make_object();
      sq.set("enabled", json::Value(sinks.sqlite.enabled));
      sq.set("path", json::Value(sinks.sqlite.path));
      sq.set("wal_mode", json::Value(sinks.sqlite.wal_mode));
      sq.set("busy_timeout_ms", json::Value(sinks.sqlite.busy_timeout_ms));
      sq.set("commit_batch_size", json::Value(sinks.sqlite.commit_batch_size));
      sq.set("commit_interval_ms", json::Value(sinks.sqlite.commit_interval_ms));
      sinks_obj.set("sqlite", std::move(sq));
   }
   {
      json::Value csv = json::Value::make_object();
      csv.set("enabled", json::Value(sinks.csv.enabled));
      csv.set("directory", json::Value(sinks.csv.directory));
      csv.set("flush_every_n_batches", json::Value(sinks.csv.flush_every_n_batches));
      sinks_obj.set("csv", std::move(csv));
   }
   {
      json::Value jl = json::Value::make_object();
      jl.set("enabled", json::Value(sinks.jsonl.enabled));
      jl.set("directory", json::Value(sinks.jsonl.directory));
      jl.set("flush_every_n_batches", json::Value(sinks.jsonl.flush_every_n_batches));
      sinks_obj.set("jsonl", std::move(jl));
   }
   {
      json::Value pg = json::Value::make_object();
      pg.set("enabled", json::Value(sinks.psql.enabled));
      pg.set("conninfo", json::Value(sinks.psql.conninfo));
      pg.set("schema", json::Value(sinks.psql.schema));
      pg.set("use_timescaledb", json::Value(sinks.psql.use_timescaledb));
      pg.set("commit_batch_size", json::Value(sinks.psql.commit_batch_size));
      sinks_obj.set("psql", std::move(pg));
   }
   {
      json::Value pr = json::Value::make_object();
      pr.set("enabled", json::Value(sinks.prometheus.enabled));
      pr.set("bind_host", json::Value(sinks.prometheus.bind_host));
      pr.set("port", json::Value(sinks.prometheus.port));
      pr.set("metric_prefix", json::Value(sinks.prometheus.metric_prefix));
      sinks_obj.set("prometheus", std::move(pr));
   }
   root.set("sinks", std::move(sinks_obj));

   json::Value gui_obj = json::Value::make_object();
   gui_obj.set("frontend", json::Value(gui.frontend));
   gui_obj.set("web_host", json::Value(gui.web_host));
   gui_obj.set("web_port", json::Value(gui.web_port));
   gui_obj.set("open_browser", json::Value(gui.open_browser));
   gui_obj.set("refresh_interval_ms", json::Value(gui.refresh_interval_ms));
   gui_obj.set("theme", json::Value(gui.theme));
   gui_obj.set("locale", json::Value(gui.locale));
   gui_obj.set("locale_file", json::Value(gui.locale_file));
   root.set("gui", std::move(gui_obj));

   return root.dump(indent);
}

void LoggerConfig::save_json_file(std::string const& path, int indent) const {
   std::filesystem::path p(path);
   if (p.has_parent_path()) {
      std::filesystem::create_directories(p.parent_path());
   }
   std::ofstream ofs(path, std::ios::out | std::ios::trunc);
   if (!ofs) {
      throw ConfigError("Unable to write configuration file: " + path);
   }
   ofs << to_json_string(indent) << "\n";
}

ValidationReport validate_config(LoggerConfig const& cfg) {
   ValidationReport report;

   if (cfg.instance_name.empty()) {
      report.errors.push_back("logger.instance_name must not be empty");
   }
   if (cfg.queue_capacity == 0) {
      report.errors.push_back("logger.queue_capacity must be >= 1");
   }
   if (cfg.duts.empty()) {
      report.errors.push_back("duts array must contain at least one sensor target configuration");
   }

   std::unordered_set<std::string> seen_names;
   for (size_t i = 0; i < cfg.duts.size(); ++i) {
      auto const& d = cfg.duts[i];
      std::string prefix = "duts[" + std::to_string(i) + "]";
      if (d.name.empty()) {
         report.errors.push_back(prefix + ".name must not be empty");
      } else if (!seen_names.insert(d.name).second) {
         report.errors.push_back("duplicate sensor target name '" + d.name + "'");
      }
      if (d.dut_ip.empty()) {
         report.errors.push_back(prefix + ".dut_ip must not be empty");
      }
      if (d.poll_interval_ms < 50) {
         report.errors.push_back(prefix + ".poll_interval_ms must be >= 50");
      }
      if (d.snmp.mode != "stub" && d.snmp.mode != "purpleair" && d.snmp.mode != "cloud" &&
          d.snmp.mode != "cloud_single" && d.snmp.mode != "cloud_multiple" &&
          d.snmp.mode != "cloud_group" && d.snmp.mode != "local" && d.snmp.mode != "ezsnmp") {
         report.errors.push_back(prefix +
                                 ".snmp.mode must be 'stub', 'purpleair', 'cloud', 'cloud_single', "
                                 "'cloud_multiple', 'cloud_group', 'local', or 'ezsnmp'");
      }
      if (d.snmp.version != "1" && d.snmp.version != "2c" && d.snmp.version != "3" &&
          d.snmp.version != "v1") {
         report.errors.push_back(prefix + ".snmp.version must be '1', '2c', '3', or 'v1'");
      }
      if (d.snmp.port < 1 || d.snmp.port > 65535) {
         report.errors.push_back(prefix + ".snmp.port must be in 1..65535");
      }
      if (d.snmp.version == "3") {
         if (d.snmp.security_username.empty()) {
            report.errors.push_back(prefix + ".snmp.security_username is required for version 3");
         }
         if (d.snmp.security_level == "authNoPriv" || d.snmp.security_level == "authPriv") {
            if (d.snmp.auth_passphrase.size() < 8) {
               report.errors.push_back(prefix +
                                       ".snmp.auth_passphrase must be at least 8 characters");
            }
         }
         if (d.snmp.security_level == "authPriv") {
            if (d.snmp.priv_passphrase.size() < 8) {
               report.errors.push_back(prefix +
                                       ".snmp.priv_passphrase must be at least 8 characters");
            }
         }
      }
      if (d.metrics.empty()) {
         report.errors.push_back(prefix + ".metrics must contain at least one metric");
      }
      for (size_t j = 0; j < d.metrics.size(); ++j) {
         auto const& m = d.metrics[j];
         std::string mprefix = prefix + ".metrics[" + std::to_string(j) + "]";
         if (m.name.empty()) {
            report.errors.push_back(mprefix + ".name must not be empty");
         }
         if (m.oid.empty()) {
            report.errors.push_back(mprefix + ".oid must not be empty");
         }
         if (m.operation != "get" && m.operation != "getnext" && m.operation != "walk" &&
             m.operation != "bulkget" && m.operation != "bulkwalk" && m.operation != "single" &&
             m.operation != "multiple" && m.operation != "history" && m.operation != "local") {
            report.errors.push_back(mprefix +
                                    ".operation must be one of: get, getnext, walk, bulkget, "
                                    "bulkwalk, single, multiple, history, local");
         }
         if (d.snmp.version == "1" && (m.operation == "bulkget" || m.operation == "bulkwalk")) {
            report.errors.push_back(mprefix + ".operation '" + m.operation +
                                    "' requires version '2c' or '3'");
         }
      }
      if (d.enabled) {
         ++report.enabled_duts;
         report.total_metrics += static_cast<int>(d.metrics.size());
      }
   }

   if (report.enabled_duts == 0 && !cfg.duts.empty()) {
      report.warnings.push_back("No enabled sensor targets in configuration");
   }

   if (cfg.sinks.sqlite.enabled) {
      ++report.enabled_sinks;
      if (cfg.sinks.sqlite.path.empty()) {
         report.errors.push_back("sinks.sqlite.path must not be empty when sqlite sink is enabled");
      }
   }
   if (cfg.sinks.csv.enabled) {
      ++report.enabled_sinks;
      if (cfg.sinks.csv.directory.empty()) {
         report.errors.push_back("sinks.csv.directory must not be empty when csv sink is enabled");
      }
   }
   if (cfg.sinks.jsonl.enabled) {
      ++report.enabled_sinks;
      if (cfg.sinks.jsonl.directory.empty()) {
         report.errors.push_back(
             "sinks.jsonl.directory must not be empty when jsonl sink is enabled");
      }
   }
   if (cfg.sinks.psql.enabled) {
      ++report.enabled_sinks;
      if (cfg.sinks.psql.conninfo.empty()) {
         report.errors.push_back("sinks.psql.conninfo must not be empty when psql sink is enabled");
      }
   }
   if (cfg.sinks.prometheus.enabled) {
      ++report.enabled_sinks;
      if (cfg.sinks.prometheus.port < 0 || cfg.sinks.prometheus.port > 65535) {
         report.errors.push_back("sinks.prometheus.port must be in 0..65535");
      }
   }

   if (report.enabled_sinks == 0) {
      report.warnings.push_back(
          "No storage sinks are enabled; polled batches will only be buffered in memory");
   }

   if (cfg.gui.frontend != "auto" && cfg.gui.frontend != "tk" && cfg.gui.frontend != "web") {
      report.errors.push_back("gui.frontend must be 'auto', 'tk', or 'web'");
   }

   report.valid = report.errors.empty();
   return report;
}

ValidationReport validate_config_json(std::string const& json_str) {
   try {
      LoggerConfig cfg = LoggerConfig::from_json_string(json_str);
      return validate_config(cfg);
   } catch (std::exception const& e) {
      ValidationReport r;
      r.valid = false;
      r.errors.push_back(e.what());
      return r;
   }
}

ValidationReport validate_config_file(std::string const& path) {
   try {
      LoggerConfig cfg = LoggerConfig::from_json_file(path);
      return validate_config(cfg);
   } catch (std::exception const& e) {
      ValidationReport r;
      r.valid = false;
      r.errors.push_back(e.what());
      return r;
   }
}

std::string generate_template_config_json(std::string const& profile) {
   LoggerConfig cfg;
   cfg.instance_name = "purpleair_data_logger_" + (profile.empty() ? "default" : profile);

   DutConfig dut1;
   dut1.name = "outdoor_patio_sensor";
   dut1.dut_ip = "api.purpleair.com";
   dut1.poll_interval_ms = 2000;
   dut1.snmp.mode = "stub";
   dut1.snmp.sensor_index = 53;
   dut1.metrics = {
       {"name", "name", "get", 25},
       {"pm2.5_atm", "pm2.5_atm", "get", 25},
       {"pm2.5_cf_1", "pm2.5_cf_1", "get", 25},
       {"pm10.0_atm", "pm10.0_atm", "get", 25},
       {"temperature", "temperature", "get", 25},
       {"humidity", "humidity", "get", 25},
       {"pressure", "pressure", "get", 25},
   };
   cfg.duts.push_back(dut1);

   if (profile == "demo" || profile == "enterprise") {
      DutConfig dut2;
      dut2.name = "indoor_living_room_sensor";
      dut2.dut_ip = "192.168.1.50";
      dut2.poll_interval_ms = 2000;
      dut2.snmp.mode = "stub";
      dut2.snmp.sensor_index = 108;
      dut2.snmp.ipv4_address = "192.168.1.50";
      dut2.metrics = {
          {"name", "name", "get", 25},
          {"pm2.5_atm", "pm2.5_atm", "get", 25},
          {"temperature", "temperature", "get", 25},
          {"humidity", "humidity", "get", 25},
          {"voc", "voc", "get", 25},
          {"rssi", "rssi", "get", 25},
      };
      cfg.duts.push_back(dut2);
      cfg.sinks.csv.enabled = true;
      cfg.sinks.jsonl.enabled = true;
      cfg.sinks.prometheus.enabled = (profile == "enterprise");
   } else if (profile == "local") {
      cfg.duts[0].name = "local_pa_ii_sensor";
      cfg.duts[0].dut_ip = "192.168.1.50";
      cfg.duts[0].snmp.mode = "local";
      cfg.duts[0].snmp.ipv4_address = "192.168.1.50";
   } else if (profile == "snmpv3") {
      cfg.duts[0].snmp.version = "3";
      cfg.duts[0].snmp.security_level = "authPriv";
      cfg.duts[0].snmp.security_username = "purpleair_monitor";
      cfg.duts[0].snmp.auth_protocol = "SHA";
      cfg.duts[0].snmp.auth_passphrase = "change_this_auth_pass";
      cfg.duts[0].snmp.priv_protocol = "AES";
      cfg.duts[0].snmp.priv_passphrase = "change_this_priv_pass";
   }

   return cfg.to_json_string(2);
}

std::string config_json_schema() {
   json::Value schema = json::Value::make_object();
   schema.set("$schema", json::Value("https://json-schema.org/draft/2020-12/schema"));
   schema.set("title", json::Value("purpleair_data_logger Configuration Schema"));
   schema.set("type", json::Value("object"));

   json::Value req = json::Value::make_array();
   req.push_back(json::Value("logger"));
   req.push_back(json::Value("duts"));
   req.push_back(json::Value("sinks"));
   schema.set("required", std::move(req));

   json::Value props = json::Value::make_object();
   json::Value logger_prop = json::Value::make_object();
   logger_prop.set("type", json::Value("object"));
   logger_prop.set("description", json::Value("Core telemetry engine runtime settings"));
   props.set("logger", std::move(logger_prop));

   json::Value duts_prop = json::Value::make_object();
   duts_prop.set("type", json::Value("array"));
   duts_prop.set(
       "description",
       json::Value("List of PurpleAir sensor targets (cloud or local) to poll via purpleair_api"));
   props.set("duts", std::move(duts_prop));

   json::Value sinks_prop = json::Value::make_object();
   sinks_prop.set("type", json::Value("object"));
   sinks_prop.set("description",
                  json::Value("Storage sinks (sqlite, csv, jsonl, psql, prometheus)"));
   props.set("sinks", std::move(sinks_prop));

   json::Value gui_prop = json::Value::make_object();
   gui_prop.set("type", json::Value("object"));
   gui_prop.set("description", json::Value("Cross-platform GUI frontend settings"));
   props.set("gui", std::move(gui_prop));

   schema.set("properties", std::move(props));
   return schema.dump(2);
}

} // namespace purpleair_data_logger
