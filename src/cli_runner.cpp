#include "purpleair_data_logger/cli_runner.h"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <thread>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/data_logger.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"
#include "purpleair_data_logger/purpleair_poller.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/version.h"

namespace purpleair_data_logger {

namespace {
struct ParsedFlags {
   std::string subcommand;
   std::string config_path;
   std::string config_json;
   std::string dut_name;
   std::string operation = "get";
   std::vector<std::string> oids;
   std::string set_type = "s";
   std::string set_value;
   std::string output_path;
   std::string profile = "minimal";
   std::string metric_filter;
   int max_repeaters = 25;
   int duration_ms = 0;
   int cycles = 0;
   int limit = 50;
   bool once = false;
   bool json_output = false;
   bool record_to_sinks = false;
   bool force = false;
   bool help = false;
};

bool is_known_subcommand(std::string const& token) {
   return token == "run" || token == "validate" || token == "probe" || token == "request" ||
          token == "set" || token == "inspect" || token == "init-config" || token == "schema" ||
          token == "version" || token == "help" || token == "gui";
}

ParsedFlags parse_args(std::vector<std::string> const& args) {
   ParsedFlags f;
   size_t i = 0;
   if (i < args.size() && !args[i].empty() && args[i][0] != '-' && is_known_subcommand(args[i])) {
      f.subcommand = args[i++];
   }
   for (; i < args.size(); ++i) {
      std::string const& a = args[i];
      if (a == "-h" || a == "--help") {
         f.help = true;
      } else if (a == "--version" || a == "-V" || a == "-v") {
         f.subcommand = "version";
      } else if (a == "--json") {
         f.json_output = true;
      } else if (a == "--once") {
         f.once = true;
      } else if (a == "--record") {
         f.record_to_sinks = true;
      } else if (a == "--force" || a == "-f") {
         f.force = true;
      } else if ((a == "-c" || a == "--config") && i + 1 < args.size()) {
         f.config_path = args[++i];
      } else if ((a == "--config-json" || a == "--config-string") && i + 1 < args.size()) {
         f.config_json = args[++i];
      } else if ((a == "-d" || a == "--dut" || a == "--sensor") && i + 1 < args.size()) {
         f.dut_name = args[++i];
      } else if ((a == "--op" || a == "--operation") && i + 1 < args.size()) {
         f.operation = args[++i];
      } else if ((a == "--oid" || a == "--field") && i + 1 < args.size()) {
         f.oids.push_back(args[++i]);
      } else if (a == "--type" && i + 1 < args.size()) {
         f.set_type = args[++i];
      } else if (a == "--value" && i + 1 < args.size()) {
         f.set_value = args[++i];
      } else if ((a == "-o" || a == "--output") && i + 1 < args.size()) {
         f.output_path = args[++i];
      } else if ((a == "--profile" || a == "--template") && i + 1 < args.size()) {
         f.profile = args[++i];
      } else if (a == "--metric" && i + 1 < args.size()) {
         f.metric_filter = args[++i];
      } else if (a == "--max-repeaters" && i + 1 < args.size()) {
         f.max_repeaters = std::atoi(args[++i].c_str());
      } else if (a == "--duration-ms" && i + 1 < args.size()) {
         f.duration_ms = std::atoi(args[++i].c_str());
      } else if (a == "--duration" && i + 1 < args.size()) {
         f.duration_ms = std::atoi(args[++i].c_str()) * 1000;
      } else if ((a == "--cycles" || a == "--max-cycles") && i + 1 < args.size()) {
         f.cycles = std::atoi(args[++i].c_str());
      } else if (a == "--limit" && i + 1 < args.size()) {
         f.limit = std::atoi(args[++i].c_str());
      } else if (!a.empty() && a[0] != '-') {
         if (f.subcommand.empty() && is_known_subcommand(a)) {
            f.subcommand = a;
         } else {
            f.oids.push_back(a);
         }
      } else {
         throw ConfigError("Unknown or incomplete CLI option: " + a);
      }
   }
   if (f.subcommand.empty()) {
      if (!f.config_path.empty() || !f.config_json.empty()) {
         f.subcommand = "run";
      } else {
         f.subcommand = "help";
      }
   }
   return f;
}

LoggerConfig load_cfg_from_flags(ParsedFlags const& f) {
   if (!f.config_json.empty()) {
      return LoggerConfig::from_json_string(f.config_json);
   }
   if (!f.config_path.empty()) {
      return LoggerConfig::from_json_file(f.config_path);
   }
   throw ConfigError("Missing required --config <file.json> or --config-json <json>");
}
} // namespace

std::string CliRunner::help_text() {
   return R"(purpleair-data-logger - High-Performance C++17 PurpleAir Telemetry Engine & CLI
Backed by purpleair_api | 100% JSON Configured | Cross-Platform Desktop & Web GUIs

Usage:
  purpleair-data-logger <subcommand> [options]

Subcommands:
  run          Run the multi-sensor PurpleAir polling & storage engine
  validate     Validate a JSON configuration file and report diagnostics
  probe        Poll one or all configured PurpleAir sensor targets once and print results
  request      Execute an ad-hoc purpleair_api operation (get, single, multiple, history, local)
  set          Execute an ad-hoc PurpleAir write operation (e.g., post_create_member)
  inspect      Query recent telemetry rows stored in configured SQLite/CSV/JSONL sinks
  init-config  Generate a starter JSON configuration file (minimal, demo, enterprise, local)
  gui          Launch the Cross-Platform GUI (drives this CLI behind the scenes)
  schema       Print the JSON Schema for purpleair_data_logger configuration files
  version      Print version and compiled feature flags
  help         Show this help message

Common Options:
  -c, --config <path>       Path to JSON configuration file
  --config-json <json>      Inline JSON configuration string
  -d, --dut <name>          Target sensor name from config (alias: --sensor)
  --once                    Poll all enabled sensor targets once, flush sinks, and exit
  --cycles <N>              Stop automatically after N polling cycles per sensor target
  --duration-ms <ms>        Run polling loop for <ms> milliseconds then stop
  --op <operation>          Operation: get, single, multiple, history, local
  --oid <field>             Field name to query (repeatable; alias: --field)
  --max-repeaters <N>       Max repeaters for bulk queries (default: 25)
  --type <type>             Value type for 'set' (i, s, d)
  --value <val>             Value to write for 'set'
  --limit <N>               Max rows to return from 'inspect' (default: 50)
  --metric <substr>         Filter 'inspect' rows by metric name substring
  --profile <name>          Template profile for 'init-config': minimal, demo, enterprise, local
  -o, --output <path>       Output file path for 'init-config' (stdout if omitted)
  --json                    Emit machine-readable JSON output
  -h, --help                Display help
)";
}

int CliRunner::run(std::vector<std::string> const& args) {
   return run_streams(args, std::cout, std::cerr);
}

CliResult CliRunner::execute(std::vector<std::string> const& args) {
   std::ostringstream out;
   std::ostringstream err;
   CliResult res;
   res.exit_code = run_streams(args, out, err);
   res.stdout_text = out.str();
   res.stderr_text = err.str();
   return res;
}

int CliRunner::run_streams(std::vector<std::string> const& args,
                           std::ostream& out,
                           std::ostream& err) {
   try {
      ParsedFlags f = parse_args(args);
      if (f.help || f.subcommand == "help") {
         out << help_text();
         return 0;
      }

      if (f.subcommand == "version") {
         if (f.json_output) {
            json::Value v = json::Value::make_object();
            v.set("version", json::Value(version()));
            v.set("calsemver_valid", json::Value(is_valid_calsemver(version())));
            v.set("purpleair_api_target_version", json::Value(purpleair_api_target_version()));
            v.set("build_info", json::Value(build_info()));
            out << v.dump(2) << "\n";
         } else {
            out << build_info() << "\n";
         }
         return 0;
      }

      if (f.subcommand == "schema") {
         out << config_json_schema() << "\n";
         return 0;
      }

      if (f.subcommand == "init-config") {
         std::string tpl = generate_template_config_json(f.profile);
         if (!f.output_path.empty()) {
            LoggerConfig cfg = LoggerConfig::from_json_string(tpl);
            cfg.save_json_file(f.output_path, 2);
            if (f.json_output) {
               json::Value v = json::Value::make_object();
               v.set("status", json::Value("written"));
               v.set("path", json::Value(f.output_path));
               v.set("profile", json::Value(f.profile));
               out << v.dump() << "\n";
            } else {
               out << "Wrote '" << f.profile << "' configuration template to " << f.output_path
                   << "\n";
            }
         } else {
            out << tpl << "\n";
         }
         return 0;
      }

      if (f.subcommand == "validate") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         ValidationReport report = validate_config(cfg);
         if (f.json_output) {
            out << report.to_json() << "\n";
         } else {
            out << "Configuration Valid: " << (report.valid ? "YES" : "NO") << "\n"
                << "  Enabled Targets : " << report.enabled_duts << "\n"
                << "  Total Metrics   : " << report.total_metrics << "\n"
                << "  Enabled Sinks   : " << report.enabled_sinks << "\n";
            for (auto const& w : report.warnings) {
               out << "  WARNING: " << w << "\n";
            }
            for (auto const& e : report.errors) {
               err << "  ERROR: " << e << "\n";
            }
         }
         return report.valid ? 0 : 2;
      }

      if (f.subcommand == "probe") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         DataLogger engine(cfg);
         std::vector<Batch> probed_batches;
         if (!f.dut_name.empty()) {
            probed_batches.push_back(engine.probe_dut(f.dut_name));
         } else {
            for (auto const& d : cfg.duts) {
               if (!d.enabled) {
                  continue;
               }
               probed_batches.push_back(engine.probe_dut(d.name));
            }
         }
         if (f.json_output) {
            json::Value root = json::Value::make_object();
            root.set("ok", json::Value(true));
            root.set("count", json::Value(static_cast<int>(probed_batches.size())));
            json::Value res_arr = json::Value::make_array();
            json::Value flat_samples = json::Value::make_array();
            for (auto const& b : probed_batches) {
               json::Value bj = json::Value::parse(b.to_json());
               res_arr.push_back(bj);
               for (auto const& s : b.samples) {
                  flat_samples.push_back(json::Value::parse(s.to_json()));
               }
            }
            if (!probed_batches.empty()) {
               root.set("dut_name", json::Value(probed_batches.front().dut_name));
               root.set("dut_ip", json::Value(probed_batches.front().dut_ip));
            }
            root.set("results", std::move(res_arr));
            root.set("samples", std::move(flat_samples));
            out << root.dump(2) << "\n";
         } else {
            for (auto const& b : probed_batches) {
               out << "Target " << b.dut_name << " (" << b.dut_ip << ") - " << b.samples.size()
                   << " samples:\n";
               for (auto const& s : b.samples) {
                  out << "  " << s.metric_name << " [" << s.oid << "." << s.oid_index << "] ("
                      << s.snmp_type << ") = " << s.raw_value << "\n";
               }
            }
         }
         return 0;
      }

      if (f.subcommand == "request") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         DataLogger engine(cfg);
         std::vector<std::string> oids = f.oids;
         if (oids.empty()) {
            std::string const target_dut =
                f.dut_name.empty() && !cfg.duts.empty() ? cfg.duts.front().name : f.dut_name;
            for (auto const& d : cfg.duts) {
               if (d.name == target_dut) {
                  for (auto const& m : d.metrics) {
                     oids.push_back(m.oid);
                  }
               }
            }
         }
         std::string resp = engine.request_json(f.dut_name, f.operation, oids, f.max_repeaters);
         if (f.record_to_sinks) {
            json::Value v = json::Value::parse(resp);
            if (v.contains("batch")) {
               engine.ingest_batch_json(v.get("batch").dump());
               engine.flush();
            }
         }
         if (f.json_output) {
            out << resp << "\n";
         } else {
            json::Value v = json::Value::parse(resp);
            out << "PurpleAir " << v.get("operation").as_string() << " on "
                << v.get("dut_name").as_string() << " (" << v.get("dut_ip").as_string() << "):\n";
            for (auto const& item : v.get("samples").as_array()) {
               out << "  " << item.get("oid").as_string() << "."
                   << item.get("oid_index").as_string() << " [" << item.get("snmp_type").as_string()
                   << "] = " << item.get("raw_value").as_string() << "\n";
            }
         }
         return 0;
      }

      if (f.subcommand == "set") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         if (f.oids.empty()) {
            throw ConfigError("'set' requires --oid <field> --type <type> --value <val>");
         }
         DataLogger engine(cfg);
         std::string resp = engine.set_json(f.dut_name, f.oids.front(), f.set_type, f.set_value);
         if (f.record_to_sinks) {
            json::Value v = json::Value::parse(resp);
            if (v.contains("batch")) {
               engine.ingest_batch_json(v.get("batch").dump());
               engine.flush();
            }
         }
         out << resp << "\n";
         return 0;
      }

      if (f.subcommand == "inspect") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         auto rows = inspect_configured_sinks(cfg, f.limit, f.dut_name, f.metric_filter);
         if (f.json_output) {
            json::Value root = json::Value::make_object();
            root.set("count", json::Value(static_cast<int>(rows.size())));
            json::Value arr = json::Value::make_array();
            for (auto const& r : rows) {
               arr.push_back(json::Value::parse(r.to_json()));
            }
            root.set("rows", std::move(arr));
            out << root.dump(2) << "\n";
         } else {
            out << "Stored Telemetry Rows (" << rows.size() << "):\n";
            for (auto const& r : rows) {
               out << "  [" << r.sink_type << "] ts=" << r.timestamp_ns << " target=" << r.dut_name
                   << " metric=" << r.metric_name << " val=" << r.value << "\n";
            }
         }
         return 0;
      }

      if (f.subcommand == "run") {
         LoggerConfig cfg = load_cfg_from_flags(f);
         if (f.cycles > 0) {
            cfg.max_poll_Cycles = f.cycles;
         }
         DataLogger engine(cfg);

         if (f.once) {
            auto batches = engine.run_once();
            if (f.json_output) {
               json::Value root = json::Value::make_object();
               root.set("event", json::Value("run_once_complete"));
               root.set("stats", json::Value::parse(engine.stats_json()));
               json::Value barr = json::Value::make_array();
               for (auto const& b : batches) {
                  barr.push_back(json::Value::parse(b.to_json()));
               }
               root.set("batches", std::move(barr));
               out << root.dump() << "\n";
            } else {
               LoggerStats st = engine.stats();
               out << "Completed single poll pass: batches=" << st.batches_written
                   << " samples=" << st.samples_written << "\n";
            }
            return 0;
         }

         engine.start();
         if (f.json_output) {
            json::Value start_ev = json::Value::make_object();
            start_ev.set("event", json::Value("started"));
            start_ev.set("instance_name", json::Value(cfg.instance_name));
            out << start_ev.dump() << "\n";
            out.flush();
         }

         auto t_start = std::chrono::steady_clock::now();
         uint64_t last_written = 0;
         while (engine.is_running()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            LoggerStats st = engine.stats();
            if (f.json_output && st.batches_written > last_written) {
               auto recent =
                   engine.recent_batches(static_cast<size_t>(st.batches_written - last_written));
               for (auto const& b : recent) {
                  json::Value bev = json::Value::make_object();
                  bev.set("event", json::Value("batch"));
                  bev.set("batch", json::Value::parse(b.to_json()));
                  bev.set("stats", json::Value::parse(st.to_json()));
                  out << bev.dump() << "\n";
               }
               out.flush();
               last_written = st.batches_written;
            }
            if (f.duration_ms > 0) {
               auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                                  std::chrono::steady_clock::now() - t_start)
                                  .count();
               if (elapsed >= f.duration_ms) {
                  engine.stop();
                  break;
               }
            }
            if (cfg.max_poll_Cycles > 0 &&
                st.batches_polled >= static_cast<uint64_t>(cfg.max_poll_Cycles) *
                                         static_cast<uint64_t>(validate_config(cfg).enabled_duts)) {
               std::this_thread::sleep_for(std::chrono::milliseconds(100));
               engine.stop();
               break;
            }
         }

         LoggerStats final_st = engine.stats();
         if (f.json_output) {
            if (final_st.batches_written > last_written) {
               auto recent = engine.recent_batches(
                   static_cast<size_t>(final_st.batches_written - last_written));
               for (auto const& b : recent) {
                  json::Value bev = json::Value::make_object();
                  bev.set("event", json::Value("batch"));
                  bev.set("batch", json::Value::parse(b.to_json()));
                  bev.set("stats", json::Value::parse(final_st.to_json()));
                  out << bev.dump() << "\n";
               }
            }
            json::Value stop_ev = json::Value::make_object();
            stop_ev.set("event", json::Value("stopped"));
            stop_ev.set("stats", json::Value::parse(final_st.to_json()));
            out << stop_ev.dump() << "\n";
            out.flush();
         } else {
            out << "Stopped purpleair-data-logger: batches_written=" << final_st.batches_written
                << " samples_written=" << final_st.samples_written << "\n";
         }
         return 0;
      }

      throw ConfigError("Unsupported subcommand: " + f.subcommand);
   } catch (std::exception const& e) {
      err << "ERROR: " << e.what() << "\n";
      return 1;
   }
}

} // namespace purpleair_data_logger
