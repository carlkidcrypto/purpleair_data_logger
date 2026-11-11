#include "purpleair_data_logger/sqlite_sink.h"

#include <chrono>
#include <filesystem>
#include <mutex>
#include <unordered_map>

#include "purpleair_data_logger/exceptions.h"

#ifdef PURPLEAIR_DL_HAVE_SQLITE3
#include <sqlite3.h>
#endif

namespace purpleair_data_logger {

struct SqliteSink::Impl {
   SqliteSinkConfig cfg;
   std::mutex mutex;
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   sqlite3* db = nullptr;
   sqlite3_stmt* stmt_insert_series = nullptr;
   sqlite3_stmt* stmt_select_series = nullptr;
   sqlite3_stmt* stmt_insert_sample = nullptr;
   std::unordered_map<std::string, int64_t> series_cache;
   bool in_transaction = false;
   int pending_samples = 0;
   std::chrono::steady_clock::time_point last_commit = std::chrono::steady_clock::now();

   void exec_sql(char const* sql) {
      char* errmsg = nullptr;
      int rc = sqlite3_exec(db, sql, nullptr, nullptr, &errmsg);
      if (rc != SQLITE_OK) {
         std::string err = errmsg ? errmsg : "sqlite3_exec failed";
         sqlite3_free(errmsg);
         throw SinkError("SQLite error: " + err);
      }
   }

   void begin_tx_if_needed() {
      if (!in_transaction) {
         exec_sql("BEGIN IMMEDIATE TRANSACTION;");
         in_transaction = true;
      }
   }

   void commit_tx_if_needed() {
      if (in_transaction) {
         exec_sql("COMMIT;");
         in_transaction = false;
         pending_samples = 0;
         last_commit = std::chrono::steady_clock::now();
      }
   }

   int64_t get_or_create_series_id(std::string const& dut_name,
                                   std::string const& dut_ip,
                                   Sample const& s) {
      std::string key =
          dut_name + "|" + dut_ip + "|" + s.metric_name + "|" + s.oid + "|" + s.oid_index;
      auto it = series_cache.find(key);
      if (it != series_cache.end()) {
         return it->second;
      }

      sqlite3_reset(stmt_insert_series);
      sqlite3_clear_bindings(stmt_insert_series);
      sqlite3_bind_text(stmt_insert_series, 1, dut_name.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_insert_series, 2, dut_ip.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_insert_series, 3, s.metric_name.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_insert_series, 4, s.oid.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_insert_series, 5, s.oid_index.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_insert_series, 6, s.snmp_type.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_step(stmt_insert_series);

      sqlite3_reset(stmt_select_series);
      sqlite3_clear_bindings(stmt_select_series);
      sqlite3_bind_text(stmt_select_series, 1, dut_name.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_select_series, 2, s.oid.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_text(stmt_select_series, 3, s.oid_index.c_str(), -1, SQLITE_TRANSIENT);

      int64_t sid = 0;
      if (sqlite3_step(stmt_select_series) == SQLITE_ROW) {
         sid = sqlite3_column_int64(stmt_select_series, 0);
      }
      series_cache[key] = sid;
      return sid;
   }
#endif
};

SqliteSink::SqliteSink(SqliteSinkConfig config) : m_impl(std::make_unique<Impl>()) {
   m_impl->cfg = std::move(config);
   if (!m_impl->cfg.enabled) {
      return;
   }
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   std::filesystem::path p(m_impl->cfg.path);
   if (p.has_parent_path()) {
      std::error_code ec;
      std::filesystem::create_directories(p.parent_path(), ec);
   }

   int rc =
       sqlite3_open_v2(m_impl->cfg.path.c_str(), &m_impl->db,
                       SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX, nullptr);
   if (rc != SQLITE_OK) {
      std::string msg = m_impl->db ? sqlite3_errmsg(m_impl->db) : "unable to open sqlite db";
      if (m_impl->db) {
         sqlite3_close(m_impl->db);
         m_impl->db = nullptr;
      }
      throw SinkError("Failed to open SQLite database '" + m_impl->cfg.path + "': " + msg);
   }

   sqlite3_busy_timeout(m_impl->db, m_impl->cfg.busy_timeout_ms);
   if (m_impl->cfg.wal_mode) {
      m_impl->exec_sql("PRAGMA journal_mode=WAL;");
   }
   m_impl->exec_sql("PRAGMA synchronous=NORMAL;");
   m_impl->exec_sql("PRAGMA temp_store=MEMORY;");

   m_impl->exec_sql(
       "CREATE TABLE IF NOT EXISTS series ("
       "  series_id INTEGER PRIMARY KEY AUTOINCREMENT,"
       "  dut_name TEXT NOT NULL,"
       "  dut_ip TEXT NOT NULL,"
       "  metric_name TEXT NOT NULL,"
       "  oid TEXT NOT NULL,"
       "  oid_index TEXT NOT NULL,"
       "  snmp_type TEXT NOT NULL,"
       "  UNIQUE(dut_name, oid, oid_index)"
       ");"
       "CREATE TABLE IF NOT EXISTS samples ("
       "  ts_ns INTEGER NOT NULL,"
       "  series_id INTEGER NOT NULL,"
       "  type_tag INTEGER NOT NULL,"
       "  val_i64 INTEGER,"
       "  val_f64 REAL,"
       "  val_str TEXT,"
       "  raw_value TEXT,"
       "  status INTEGER NOT NULL,"
       "  FOREIGN KEY(series_id) REFERENCES series(series_id)"
       ");"
       "CREATE INDEX IF NOT EXISTS idx_samples_series_ts ON samples(series_id, ts_ns);");

   char const* sql_ins_series =
       "INSERT OR IGNORE INTO series(dut_name, dut_ip, metric_name, oid, oid_index, snmp_type) "
       "VALUES (?1, ?2, ?3, ?4, ?5, ?6);";
   if (sqlite3_prepare_v2(m_impl->db, sql_ins_series, -1, &m_impl->stmt_insert_series, nullptr) !=
       SQLITE_OK) {
      throw SinkError("Failed to prepare insert_series statement");
   }

   char const* sql_sel_series =
       "SELECT series_id FROM series WHERE dut_name=?1 AND oid=?2 AND oid_index=?3;";
   if (sqlite3_prepare_v2(m_impl->db, sql_sel_series, -1, &m_impl->stmt_select_series, nullptr) !=
       SQLITE_OK) {
      throw SinkError("Failed to prepare select_series statement");
   }

   char const* sql_ins_sample =
       "INSERT INTO samples(ts_ns, series_id, type_tag, val_i64, val_f64, val_str, raw_value, "
       "status) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8);";
   if (sqlite3_prepare_v2(m_impl->db, sql_ins_sample, -1, &m_impl->stmt_insert_sample, nullptr) !=
       SQLITE_OK) {
      throw SinkError("Failed to prepare insert_sample statement");
   }
#else
   throw SinkError("SQLite3 support was not compiled into purpleair_data_logger");
#endif
}

SqliteSink::~SqliteSink() {
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   try {
      flush();
   } catch (...) {
   }
   if (m_impl->stmt_insert_series) {
      sqlite3_finalize(m_impl->stmt_insert_series);
   }
   if (m_impl->stmt_select_series) {
      sqlite3_finalize(m_impl->stmt_select_series);
   }
   if (m_impl->stmt_insert_sample) {
      sqlite3_finalize(m_impl->stmt_insert_sample);
   }
   if (m_impl->db) {
      sqlite3_close(m_impl->db);
   }
#endif
}

void SqliteSink::write_batch(Batch const& batch) {
   if (!m_impl->cfg.enabled) {
      return;
   }
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   std::lock_guard<std::mutex> lock(m_impl->mutex);
   m_impl->begin_tx_if_needed();

   for (auto const& s : batch.samples) {
      int64_t sid = m_impl->get_or_create_series_id(batch.dut_name, batch.dut_ip, s);

      sqlite3_reset(m_impl->stmt_insert_sample);
      sqlite3_clear_bindings(m_impl->stmt_insert_sample);
      sqlite3_bind_int64(m_impl->stmt_insert_sample, 1, batch.timestamp_ns);
      sqlite3_bind_int64(m_impl->stmt_insert_sample, 2, sid);
      sqlite3_bind_int(m_impl->stmt_insert_sample, 3, static_cast<int>(s.type_tag));

      if (s.type_tag == TypeTag::Int64) {
         sqlite3_bind_int64(m_impl->stmt_insert_sample, 4, s.i64);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 5);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 6);
      } else if (s.type_tag == TypeTag::Float64) {
         sqlite3_bind_null(m_impl->stmt_insert_sample, 4);
         sqlite3_bind_double(m_impl->stmt_insert_sample, 5, s.f64);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 6);
      } else if (s.type_tag == TypeTag::Str) {
         sqlite3_bind_null(m_impl->stmt_insert_sample, 4);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 5);
         sqlite3_bind_text(m_impl->stmt_insert_sample, 6, s.str_val.c_str(), -1, SQLITE_TRANSIENT);
      } else {
         sqlite3_bind_null(m_impl->stmt_insert_sample, 4);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 5);
         sqlite3_bind_null(m_impl->stmt_insert_sample, 6);
      }

      sqlite3_bind_text(m_impl->stmt_insert_sample, 7, s.raw_value.c_str(), -1, SQLITE_TRANSIENT);
      sqlite3_bind_int(m_impl->stmt_insert_sample, 8, static_cast<int>(s.status));

      if (sqlite3_step(m_impl->stmt_insert_sample) != SQLITE_DONE) {
         throw SinkError(std::string("SQLite sample insert failed: ") + sqlite3_errmsg(m_impl->db));
      }
      ++m_impl->pending_samples;
   }

   auto elapsed_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                         std::chrono::steady_clock::now() - m_impl->last_commit)
                         .count();
   if (m_impl->pending_samples >= m_impl->cfg.commit_batch_size ||
       elapsed_ms >= m_impl->cfg.commit_interval_ms) {
      m_impl->commit_tx_if_needed();
   }
#endif
}

void SqliteSink::flush() {
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   std::lock_guard<std::mutex> lock(m_impl->mutex);
   m_impl->commit_tx_if_needed();
#endif
}

} // namespace purpleair_data_logger
