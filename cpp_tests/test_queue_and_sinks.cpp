#include <gtest/gtest.h>

#include <chrono>
#include <string>
#include <thread>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

#include <sqlite3.h>

#include "purpleair_data_logger/csv_sink.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/jsonl_sink.h"
#include "purpleair_data_logger/prometheus_sink.h"
#include "purpleair_data_logger/psql_sink.h"
#include "purpleair_data_logger/queue.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/sqlite_sink.h"
#include "test_common.h"

using namespace purpleair_data_logger;

TEST(BoundedQueueTest, AllQueueOperationsAndTimeouts) {
   BoundedQueue<int> q0(0);
   EXPECT_EQ(q0.capacity(), 1u);
   EXPECT_FALSE(q0.is_closed());

   EXPECT_TRUE(q0.push_wait(100, std::chrono::milliseconds(10)));
   EXPECT_EQ(q0.size(), 1u);
   EXPECT_FALSE(q0.push_wait(200, std::chrono::milliseconds(5)));

   auto v = q0.pop_wait(std::chrono::milliseconds(10));
   ASSERT_TRUE(v.has_value());
   EXPECT_EQ(*v, 100);
   EXPECT_FALSE(q0.pop_wait(std::chrono::milliseconds(5)).has_value());

   q0.close();
   EXPECT_TRUE(q0.is_closed());
   EXPECT_FALSE(q0.push_wait(300, std::chrono::milliseconds(5)));
   EXPECT_FALSE(q0.pop_wait(std::chrono::milliseconds(5)).has_value());
   q0.reopen();
   EXPECT_FALSE(q0.is_closed());
}

TEST(CsvAndJsonlSinksTest, DisabledEnabledEscapingAndFlush) {
   purpleair_dl_test::TempDir tmp("csv_jsonl");

   Batch b;
   b.dut_name = "sensor/with*special?chars";
   b.dut_ip = "10.0.0.1";
   b.timestamp_ns = 1700000000000LL;
   b.samples.push_back(Sample::from_purpleair_field("int_m", "oid1", "1", "INTEGER", "42"));
   b.samples.push_back(Sample::from_purpleair_field("flt_m", "oid2", "1", "FLOAT", "3.5"));
   b.samples.push_back(
       Sample::from_purpleair_field("str,q", "oid\"3", "1", "STRING", "hello, \"world\"\nline2"));
   b.samples.push_back(
       Sample::from_purpleair_field("null_m", "oid4", "1", "NOSUCHINSTANCE", "No Such Instance"));

   Batch b_empty_name = b;
   b_empty_name.dut_name = "";

   // Disabled CSV & JSONL sinks should no-op
   CsvSinkConfig csv_dis;
   csv_dis.enabled = false;
   CsvSink s_csv_dis(csv_dis);
   s_csv_dis.write_batch(b);
   s_csv_dis.flush();

   JsonlSinkConfig jl_dis;
   jl_dis.enabled = false;
   JsonlSink s_jl_dis(jl_dis);
   s_jl_dis.write_batch(b);
   s_jl_dis.flush();

   // Enabled CSV & JSONL sinks with batch buffering
   CsvSinkConfig csv_en;
   csv_en.enabled = true;
   csv_en.directory = (tmp.path() / "csv").string();
   csv_en.flush_every_n_batches = 2;
   CsvSink s_csv(csv_en);
   EXPECT_EQ(s_csv.name(), "csv");
   s_csv.write_batch(b);
   s_csv.write_batch(b);
   s_csv.write_batch(b_empty_name);
   s_csv.flush();

   // File open failure: create a directory named "blocked_sensor.csv" inside csv dir
   std::filesystem::create_directories(tmp.path() / "csv" / "blocked_sensor.csv");
   Batch b_blocked = b;
   b_blocked.dut_name = "blocked_sensor";
   EXPECT_THROW(s_csv.write_batch(b_blocked), SinkError);

   // Directory creation failure
   CsvSinkConfig csv_bad_dir;
   csv_bad_dir.enabled = true;
   csv_bad_dir.directory = (tmp.path() / "csv" / "sensor.csv" / "invalid").string();
   EXPECT_THROW({ CsvSink s_bad(csv_bad_dir); }, SinkError);

   JsonlSinkConfig jl_en;
   jl_en.enabled = true;
   jl_en.directory = (tmp.path() / "jsonl").string();
   jl_en.flush_every_n_batches = 2;
   JsonlSink s_jl(jl_en);
   EXPECT_EQ(s_jl.name(), "jsonl");
   s_jl.write_batch(b);
   s_jl.write_batch(b);
   s_jl.write_batch(b_empty_name);
   s_jl.flush();

   std::filesystem::create_directories(tmp.path() / "jsonl" / "blocked_sensor.jsonl");
   EXPECT_THROW(s_jl.write_batch(b_blocked), SinkError);

   JsonlSinkConfig jl_bad_dir;
   jl_bad_dir.enabled = true;
   jl_bad_dir.directory = (tmp.path() / "jsonl" / "sensor.jsonl" / "invalid").string();
   EXPECT_THROW({ JsonlSink s_jl_bad(jl_bad_dir); }, SinkError);
}

TEST(SqliteAndPsqlSinksTest, TransactionsTypesAndErrorPaths) {
   purpleair_dl_test::TempDir tmp("sqlite_psql");

   Batch b;
   b.dut_name = "pa-node";
   b.dut_ip = "127.0.0.1";
   b.timestamp_ns = 1700000005000LL;
   b.samples.push_back(Sample::from_purpleair_field("i_m", "i", "53", "INTEGER", "10"));
   b.samples.push_back(Sample::from_purpleair_field("f_m", "f", "53", "FLOAT", "20.5"));
   b.samples.push_back(Sample::from_purpleair_field("s_m", "s", "53", "STRING", "text"));
   b.samples.push_back(
       Sample::from_purpleair_field("n_m", "n", "53", "NOSUCHOBJECT", "No Such Object"));

   // Disabled SQLite sink
   SqliteSinkConfig sq_dis;
   sq_dis.enabled = false;
   SqliteSink s_sq_dis(sq_dis);
   s_sq_dis.write_batch(b);
   s_sq_dis.flush();

   // Enabled SQLite sink
   SqliteSinkConfig sq_en;
   sq_en.enabled = true;
   sq_en.path = (tmp.path() / "nested" / "db.sqlite3").string();
   sq_en.wal_mode = true;
   sq_en.commit_batch_size = 2;
   SqliteSink s_sq(sq_en);
   EXPECT_EQ(s_sq.name(), "sqlite");
   s_sq.write_batch(b);
   // Second write hits series_cache!
   s_sq.write_batch(b);
   s_sq.flush();

   // Invalid SQLite path (directory as file path)
   SqliteSinkConfig sq_bad;
   sq_bad.enabled = true;
   sq_bad.path = tmp.path().string();
   EXPECT_THROW(SqliteSink{sq_bad}, SinkError);

   // SQLite error in exec_sql (conflicting table schema triggers index error)
   std::string bad_exec_db = (tmp.path() / "bad_exec.db").string();
   {
      sqlite3* db = nullptr;
      sqlite3_open(bad_exec_db.c_str(), &db);
      sqlite3_exec(db, "CREATE TABLE samples(dummy INT);", nullptr, nullptr, nullptr);
      sqlite3_close(db);
   }
   SqliteSinkConfig sq_bad_exec;
   sq_bad_exec.enabled = true;
   sq_bad_exec.path = bad_exec_db;
   EXPECT_THROW(SqliteSink{sq_bad_exec}, SinkError);

   // SQLite error in prepare statements (conflicting series schema)
   std::string bad_schema_db = (tmp.path() / "bad_schema.db").string();
   {
      sqlite3* db = nullptr;
      sqlite3_open(bad_schema_db.c_str(), &db);
      sqlite3_exec(db, "CREATE TABLE series(dummy INT);", nullptr, nullptr, nullptr);
      sqlite3_close(db);
   }
   SqliteSinkConfig sq_bad_schema;
   sq_bad_schema.enabled = true;
   sq_bad_schema.path = bad_schema_db;
   EXPECT_THROW(SqliteSink{sq_bad_schema}, SinkError);

   // insert_series prepares, but select_series fails (series table lacks series_id)
   std::string bad_select_db = (tmp.path() / "bad_select.db").string();
   {
      sqlite3* db = nullptr;
      sqlite3_open(bad_select_db.c_str(), &db);
      sqlite3_exec(db,
                   "CREATE TABLE series(dut_name TEXT, dut_ip TEXT, metric_name TEXT, oid TEXT, "
                   "oid_index TEXT, snmp_type TEXT);",
                   nullptr, nullptr, nullptr);
      sqlite3_close(db);
   }
   SqliteSinkConfig sq_bad_select;
   sq_bad_select.enabled = true;
   sq_bad_select.path = bad_select_db;
   EXPECT_THROW(SqliteSink{sq_bad_select}, SinkError);

   // series statements prepare, but insert_sample fails (samples table lacks value columns)
   std::string bad_sample_db = (tmp.path() / "bad_sample.db").string();
   {
      sqlite3* db = nullptr;
      sqlite3_open(bad_sample_db.c_str(), &db);
      sqlite3_exec(db, "CREATE TABLE samples(ts_ns INTEGER, series_id INTEGER);", nullptr, nullptr,
                   nullptr);
      sqlite3_close(db);
   }
   SqliteSinkConfig sq_bad_sample;
   sq_bad_sample.enabled = true;
   sq_bad_sample.path = bad_sample_db;
   EXPECT_THROW(SqliteSink{sq_bad_sample}, SinkError);

   // SQLite error in sqlite3_step (trigger that aborts insert)
   std::string trigger_db = (tmp.path() / "trigger.db").string();
   SqliteSinkConfig sq_trig_cfg;
   sq_trig_cfg.enabled = true;
   sq_trig_cfg.path = trigger_db;
   {
      SqliteSink sq_trig(sq_trig_cfg);
      sq_trig.write_batch(b);
      sq_trig.flush();
   }
   {
      sqlite3* db = nullptr;
      sqlite3_open(trigger_db.c_str(), &db);
      sqlite3_exec(db,
                   "CREATE TRIGGER fail_ins BEFORE INSERT ON samples BEGIN SELECT RAISE(ABORT, "
                   "'forced'); END;",
                   nullptr, nullptr, nullptr);
      sqlite3_close(db);
   }
   SqliteSink sq_failing(sq_trig_cfg);
   EXPECT_THROW(sq_failing.write_batch(b), SinkError);

   // Disabled PsqlSink
   PsqlSinkConfig pg_dis;
   pg_dis.enabled = false;
   PsqlSink s_pg_dis(pg_dis);
   EXPECT_EQ(s_pg_dis.name(), "psql");
   s_pg_dis.write_batch(b);
   s_pg_dis.flush();

   // Enabled PsqlSink with unreachable conninfo throws SinkError
   PsqlSinkConfig pg_en;
   pg_en.enabled = true;
   pg_en.conninfo = "host=127.0.0.1 port=1 dbname=nonexistent connect_timeout=1";
   EXPECT_THROW(PsqlSink{pg_en}, SinkError);

   // PsqlSink stub and error testing
   PsqlSinkConfig pg_stub;
   pg_stub.enabled = true;
   pg_stub.conninfo = "stub_for_testing";
   PsqlSink s_pg_stub(pg_stub);
   s_pg_stub.write_batch(b);
   s_pg_stub.flush();

   PsqlSinkConfig pg_ins_err;
   pg_ins_err.enabled = true;
   pg_ins_err.conninfo = "stub_insert_error";
   PsqlSink s_pg_ins_err(pg_ins_err);
   EXPECT_THROW(s_pg_ins_err.write_batch(b), SinkError);

   PsqlSinkConfig pg_sch_err;
   pg_sch_err.enabled = true;
   pg_sch_err.conninfo = "stub_schema_error";
   EXPECT_THROW(PsqlSink{pg_sch_err}, SinkError);
}

TEST(PrometheusSinkTest, ScrapeEndpointAndMetricFormatting) {
   Batch b;
   b.dut_name = "pa\"dut\\1\n";
   b.dut_ip = "127.0.0.1";
   b.timestamp_ns = 1700000009000LL;
   b.samples.push_back(Sample::from_purpleair_field("25_pm.atm", "pm2.5", "53", "FLOAT", "15.5"));
   b.samples.push_back(Sample::from_purpleair_field("humidity", "hum", "53", "INTEGER", "60"));
   b.samples.push_back(Sample::from_purpleair_field("label", "name", "53", "STRING", "ignored"));

   PrometheusSinkConfig pr_dis;
   pr_dis.enabled = false;
   PrometheusSink s_dis(pr_dis);
   s_dis.write_batch(b);
   s_dis.flush();

   PrometheusSinkConfig pr_en;
   pr_en.enabled = true;
   pr_en.bind_host = "invalid_ip_falls_back_to_loopback";
   pr_en.port = 0;
   pr_en.metric_prefix = "99_pa-dl";
   PrometheusSink s_en(pr_en);
   EXPECT_EQ(s_en.name(), "prometheus");
   s_en.write_batch(b);
   s_en.flush();

   std::string rendered = s_en.render_metrics();
   EXPECT_NE(rendered.find("_99_pa_dl_batches_total 1"), std::string::npos);
   EXPECT_NE(rendered.find("_99_pa_dl__25_pm_atm"), std::string::npos);

   int port = s_en.bound_port();
   if (port > 0) {
      int fd = static_cast<int>(::socket(AF_INET, SOCK_STREAM, 0));
      if (fd >= 0) {
         sockaddr_in addr{};
         addr.sin_family = AF_INET;
         addr.sin_port = htons(static_cast<uint16_t>(port));
         inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);
         if (::connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0) {
            std::string req = "GET /metrics HTTP/1.1\r\nHost: localhost\r\n\r\n";
#ifdef _WIN32
            ::send(fd, req.data(), static_cast<int>(req.size()), 0);
#else
            (void)::write(fd, req.data(), req.size());
#endif
            char buf[4096]{};
#ifdef _WIN32
            int n = ::recv(fd, buf, sizeof(buf) - 1, 0);
#else
            ssize_t n = ::read(fd, buf, sizeof(buf) - 1);
#endif
            if (n > 0) {
               std::string http_resp(buf, static_cast<size_t>(n));
               EXPECT_NE(http_resp.find("HTTP/1.1 200 OK"), std::string::npos);
            }
         }
#ifdef _WIN32
         closesocket(fd);
#else
         ::close(fd);
#endif
      }
   }

   // Allow at least one 100ms select() timeout iteration before stop_server()
   std::this_thread::sleep_for(std::chrono::milliseconds(150));

   // Port collision / bind error handling
   PrometheusSinkConfig pr_bad;
   pr_bad.enabled = true;
   pr_bad.port = 1; // Privileged port requires root
   pr_bad.bind_host = "127.0.0.1";
   PrometheusSink s_pr_bad(pr_bad);
   EXPECT_EQ(s_pr_bad.bound_port(), 0);

   // Non-local RFC 5737 TEST-NET-3 address deterministically fails bind() across OSes
   PrometheusSinkConfig pr_unavail;
   pr_unavail.enabled = true;
   pr_unavail.port = 0;
   pr_unavail.bind_host = "203.0.113.1";
   PrometheusSink s_pr_unavail(pr_unavail);
   EXPECT_EQ(s_pr_unavail.bound_port(), 0);
}
