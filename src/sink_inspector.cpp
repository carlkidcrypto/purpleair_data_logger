#include <algorithm>
#include <filesystem>
#include <fstream>
#include <sstream>

#include "purpleair_data_logger/csv_sink.h"
#include "purpleair_data_logger/json_utils.h"
#include "purpleair_data_logger/jsonl_sink.h"
#include "purpleair_data_logger/prometheus_sink.h"
#include "purpleair_data_logger/psql_sink.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/sqlite_sink.h"

#ifdef PURPLEAIR_DL_HAVE_SQLITE3
#include <sqlite3.h>
#endif

namespace purpleair_data_logger {

std::vector<std::unique_ptr<ISink>> create_sinks(SinksConfig const& cfg) {
   std::vector<std::unique_ptr<ISink>> out;
   if (cfg.sqlite.enabled) {
      out.push_back(std::make_unique<SqliteSink>(cfg.sqlite));
   }
   if (cfg.csv.enabled) {
      out.push_back(std::make_unique<CsvSink>(cfg.csv));
   }
   if (cfg.jsonl.enabled) {
      out.push_back(std::make_unique<JsonlSink>(cfg.jsonl));
   }
   if (cfg.psql.enabled) {
      out.push_back(std::make_unique<PsqlSink>(cfg.psql));
   }
   if (cfg.prometheus.enabled) {
      out.push_back(std::make_unique<PrometheusSink>(cfg.prometheus));
   }
   return out;
}

namespace {
bool matches_filter(std::string const& val, std::string const& filter) {
   if (filter.empty()) {
      return true;
   }
   return val.find(filter) != std::string::npos;
}

std::vector<std::string> split_csv_line(std::string const& line) {
   std::vector<std::string> fields;
   std::string cur;
   bool in_quotes = false;
   for (size_t i = 0; i < line.size(); ++i) {
      char c = line[i];
      if (in_quotes) {
         if (c == '"') {
            if (i + 1 < line.size() && line[i + 1] == '"') {
               cur.push_back('"');
               ++i;
            } else {
               in_quotes = false;
            }
         } else {
            cur.push_back(c);
         }
      } else {
         if (c == '"') {
            in_quotes = true;
         } else if (c == ',') {
            fields.push_back(cur);
            cur.clear();
         } else if (c != '\r') {
            cur.push_back(c);
         }
      }
   }
   fields.push_back(cur);
   return fields;
}
} // namespace

std::vector<SinkRow> inspect_configured_sinks(LoggerConfig const& cfg,
                                              int limit,
                                              std::string const& dut_filter,
                                              std::string const& metric_filter) {
   if (limit <= 0) {
      limit = 100;
   }
   std::vector<SinkRow> rows;

#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   if (cfg.sinks.sqlite.enabled && std::filesystem::exists(cfg.sinks.sqlite.path)) {
      sqlite3* db = nullptr;
      if (sqlite3_open_v2(cfg.sinks.sqlite.path.c_str(), &db, SQLITE_OPEN_READONLY, nullptr) ==
          SQLITE_OK) {
         char const* sql =
             "SELECT p.ts_ns, s.dut_name, s.dut_ip, s.metric_name, s.oid, s.oid_index, "
             "s.snmp_type, COALESCE(CAST(p.val_i64 AS TEXT), CAST(p.val_f64 AS TEXT), p.val_str, "
             "p.raw_value, ''), COALESCE(p.raw_value, ''), p.status "
             "FROM samples p JOIN series s ON p.series_id = s.series_id "
             "ORDER BY p.ts_ns DESC LIMIT ?1;";
         sqlite3_stmt* stmt = nullptr;
         if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
            sqlite3_bind_int(stmt, 1, limit * 4);
            while (sqlite3_step(stmt) == SQLITE_ROW && static_cast<int>(rows.size()) < limit) {
               SinkRow r;
               r.sink_type = "sqlite";
               r.timestamp_ns = sqlite3_column_int64(stmt, 0);
               char const* c1 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 1));
               char const* c2 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 2));
               char const* c3 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 3));
               char const* c4 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 4));
               char const* c5 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 5));
               char const* c6 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 6));
               char const* c7 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 7));
               char const* c8 = reinterpret_cast<char const*>(sqlite3_column_text(stmt, 8));
               r.dut_name = c1 ? c1 : "";
               r.dut_ip = c2 ? c2 : "";
               r.metric_name = c3 ? c3 : "";
               r.oid = c4 ? c4 : "";
               r.oid_index = c5 ? c5 : "";
               r.snmp_type = c6 ? c6 : "";
               r.value = c7 ? c7 : "";
               r.raw_value = c8 ? c8 : "";
               r.status = sqlite3_column_int(stmt, 9);
               if (matches_filter(r.dut_name, dut_filter) &&
                   matches_filter(r.metric_name, metric_filter)) {
                  rows.push_back(std::move(r));
               }
            }
            sqlite3_finalize(stmt);
         }
      }
      if (db) {
         sqlite3_close(db);
      }
   }
#endif

   if (static_cast<int>(rows.size()) < limit && cfg.sinks.jsonl.enabled &&
       std::filesystem::is_directory(cfg.sinks.jsonl.directory)) {
      for (auto const& entry : std::filesystem::directory_iterator(cfg.sinks.jsonl.directory)) {
         if (!entry.is_regular_file() || entry.path().extension() != ".jsonl") {
            continue;
         }
         std::ifstream ifs(entry.path());
         std::string line;
         while (std::getline(ifs, line) && static_cast<int>(rows.size()) < limit) {
            if (line.empty()) {
               continue;
            }
            try {
               Batch b = Batch::from_json(line);
               for (auto const& s : b.samples) {
                  if (!matches_filter(b.dut_name, dut_filter) ||
                      !matches_filter(s.metric_name, metric_filter)) {
                     continue;
                  }
                  SinkRow r;
                  r.sink_type = "jsonl";
                  r.timestamp_ns = b.timestamp_ns;
                  r.dut_name = b.dut_name;
                  r.dut_ip = b.dut_ip;
                  r.metric_name = s.metric_name;
                  r.oid = s.oid;
                  r.oid_index = s.oid_index;
                  r.snmp_type = s.snmp_type;
                  r.value = s.raw_value;
                  r.raw_value = s.raw_value;
                  r.status = static_cast<int>(s.status);
                  rows.push_back(std::move(r));
                  if (static_cast<int>(rows.size()) >= limit) {
                     break;
                  }
               }
            } catch (...) {
            }
         }
      }
   }

   if (static_cast<int>(rows.size()) < limit && cfg.sinks.csv.enabled &&
       std::filesystem::is_directory(cfg.sinks.csv.directory)) {
      for (auto const& entry : std::filesystem::directory_iterator(cfg.sinks.csv.directory)) {
         if (!entry.is_regular_file() || entry.path().extension() != ".csv") {
            continue;
         }
         std::ifstream ifs(entry.path());
         std::string line;
         bool first = true;
         while (std::getline(ifs, line) && static_cast<int>(rows.size()) < limit) {
            if (first) {
               first = false;
               continue;
            }
            auto cols = split_csv_line(line);
            if (cols.size() < 11) {
               continue;
            }
            SinkRow r;
            r.sink_type = "csv";
            r.timestamp_ns = std::strtoll(cols[0].c_str(), nullptr, 10);
            r.dut_name = cols[1];
            r.dut_ip = cols[2];
            r.metric_name = cols[3];
            r.oid = cols[4];
            r.oid_index = cols[5];
            r.snmp_type = cols[6];
            r.value = cols[8];
            r.raw_value = cols[9];
            r.status = std::atoi(cols[10].c_str());
            if (matches_filter(r.dut_name, dut_filter) &&
                matches_filter(r.metric_name, metric_filter)) {
               rows.push_back(std::move(r));
            }
         }
      }
   }

   return rows;
}

} // namespace purpleair_data_logger
