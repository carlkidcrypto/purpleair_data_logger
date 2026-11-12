#include <gtest/gtest.h>

#include <chrono>
#include <string>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

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
   s_csv.write_batch(b);
   s_csv.write_batch(b);
   s_csv.write_batch(b_empty_name);
   s_csv.flush();

   JsonlSinkConfig jl_en;
   jl_en.enabled = true;
   jl_en.directory = (tmp.path() / "jsonl").string();
   jl_en.flush_every_n_batches = 2;
   JsonlSink s_jl(jl_en);
   s_jl.write_batch(b);
   s_jl.write_batch(b);
   s_jl.write_batch(b_empty_name);
   s_jl.flush();
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
   s_sq.write_batch(b);
   // Second write hits series_cache!
   s_sq.write_batch(b);
   s_sq.flush();

   // Invalid SQLite path (directory as file path)
   SqliteSinkConfig sq_bad;
   sq_bad.enabled = true;
   sq_bad.path = tmp.path().string();
   EXPECT_THROW(SqliteSink{sq_bad}, SinkError);

   // Disabled PsqlSink
   PsqlSinkConfig pg_dis;
   pg_dis.enabled = false;
   PsqlSink s_pg_dis(pg_dis);
   s_pg_dis.write_batch(b);
   s_pg_dis.flush();

   // Enabled PsqlSink with unreachable conninfo throws SinkError
   PsqlSinkConfig pg_en;
   pg_en.enabled = true;
   pg_en.conninfo = "host=127.0.0.1 port=1 dbname=nonexistent connect_timeout=1";
   EXPECT_THROW(PsqlSink{pg_en}, SinkError);
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
}
