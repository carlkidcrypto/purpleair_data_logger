#include "purpleair_data_logger/psql_sink.h"

#include <mutex>

#include "purpleair_data_logger/exceptions.h"

#ifdef PURPLEAIR_DL_HAVE_LIBPQ
#include <libpq-fe.h>
#endif

namespace purpleair_data_logger {

struct PsqlSink::Impl {
   PsqlSinkConfig cfg;
   std::mutex mutex;
#ifdef PURPLEAIR_DL_HAVE_LIBPQ
   PGconn* conn = nullptr;
#endif
};

PsqlSink::PsqlSink(PsqlSinkConfig config) : m_impl(std::make_unique<Impl>()) {
   m_impl->cfg = std::move(config);
   if (!m_impl->cfg.enabled) {
      return;
   }
#ifdef PURPLEAIR_DL_HAVE_LIBPQ
   m_impl->conn = PQconnectdb(m_impl->cfg.conninfo.c_str());
   if (PQstatus(m_impl->conn) != CONNECTION_OK) {
      std::string err = PQerrorMessage(m_impl->conn);
      PQfinish(m_impl->conn);
      m_impl->conn = nullptr;
      throw SinkError("PostgreSQL connection failed: " + err);
   }
   PGresult* res = PQexec(m_impl->conn,
                          "CREATE TABLE IF NOT EXISTS purpleair_samples ("
                          "  ts_ns BIGINT NOT NULL,"
                          "  dut_name TEXT NOT NULL,"
                          "  dut_ip TEXT NOT NULL,"
                          "  metric_name TEXT NOT NULL,"
                          "  oid TEXT NOT NULL,"
                          "  oid_index TEXT NOT NULL,"
                          "  snmp_type TEXT NOT NULL,"
                          "  type_tag INT NOT NULL,"
                          "  val_i64 BIGINT,"
                          "  val_f64 DOUBLE PRECISION,"
                          "  val_str TEXT,"
                          "  raw_value TEXT,"
                          "  status INT NOT NULL"
                          ");");
   if (PQresultStatus(res) != PGRES_COMMAND_OK) {
      std::string err = PQerrorMessage(m_impl->conn);
      PQclear(res);
      throw SinkError("PostgreSQL schema creation failed: " + err);
   }
   PQclear(res);
#else
   throw SinkError("PostgreSQL libpq support was not compiled into purpleair_data_logger");
#endif
}

PsqlSink::~PsqlSink() {
#ifdef PURPLEAIR_DL_HAVE_LIBPQ
   if (m_impl && m_impl->conn) {
      PQfinish(m_impl->conn);
      m_impl->conn = nullptr;
   }
#endif
}

void PsqlSink::write_batch(Batch const& batch) {
   if (!m_impl->cfg.enabled) {
      return;
   }
#ifdef PURPLEAIR_DL_HAVE_LIBPQ
   std::lock_guard<std::mutex> lock(m_impl->mutex);
   char const* sql =
       "INSERT INTO purpleair_samples(ts_ns, dut_name, dut_ip, metric_name, oid, oid_index, "
       "snmp_type, type_tag, val_i64, val_f64, val_str, raw_value, status) "
       "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);";
   for (auto const& s : batch.samples) {
      std::string ts = std::to_string(batch.timestamp_ns);
      std::string ttag = std::to_string(static_cast<int>(s.type_tag));
      std::string i64s = std::to_string(s.i64);
      std::string f64s = std::to_string(s.f64);
      std::string st = std::to_string(static_cast<int>(s.status));

      char const* values[13] = {
          ts.c_str(),
          batch.dut_name.c_str(),
          batch.dut_ip.c_str(),
          s.metric_name.c_str(),
          s.oid.c_str(),
          s.oid_index.c_str(),
          s.snmp_type.c_str(),
          ttag.c_str(),
          s.type_tag == TypeTag::Int64 ? i64s.c_str() : nullptr,
          s.type_tag == TypeTag::Float64 ? f64s.c_str() : nullptr,
          s.type_tag == TypeTag::Str ? s.str_val.c_str() : nullptr,
          s.raw_value.c_str(),
          st.c_str(),
      };
      PGresult* res = PQexecParams(m_impl->conn, sql, 13, nullptr, values, nullptr, nullptr, 0);
      if (PQresultStatus(res) != PGRES_COMMAND_OK) {
         std::string err = PQerrorMessage(m_impl->conn);
         PQclear(res);
         throw SinkError("PostgreSQL insert failed: " + err);
      }
      PQclear(res);
   }
#else
   (void)batch;
#endif
}

void PsqlSink::flush() {}

} // namespace purpleair_data_logger
