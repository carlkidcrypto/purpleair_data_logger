#include <gtest/gtest.h>

#include <atomic>
#include <chrono>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <string>
#include <thread>
#include <vector>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

#include "purpleair_data_logger/cli_runner.h"
#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/csv_sink.h"
#include "purpleair_data_logger/data_logger.h"
#include "purpleair_data_logger/datatypes.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"
#include "purpleair_data_logger/jsonl_sink.h"
#include "purpleair_data_logger/prometheus_sink.h"
#include "purpleair_data_logger/psql_sink.h"
#include "purpleair_data_logger/purpleair_poller.h"
#include "purpleair_data_logger/queue.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/sqlite_sink.h"
#include "purpleair_data_logger/version.h"

namespace purpleair_data_logger {
namespace {

class TempDir {
  public:
   explicit TempDir(std::string const& prefix) {
      auto base = std::filesystem::temp_directory_path();
      auto ts = std::chrono::steady_clock::now().time_since_epoch().count();
      m_path = base / (prefix + "_" + std::to_string(ts));
      std::filesystem::create_directories(m_path);
   }
   ~TempDir() {
      std::error_code ec;
      std::filesystem::remove_all(m_path, ec);
   }
   std::filesystem::path const& path() const { return m_path; }

  private:
   std::filesystem::path m_path;
};

// Lightweight loopback HTTP server serving a mock PurpleAir local sensor /json payload
class LoopbackHttpJsonServer {
  public:
   explicit LoopbackHttpJsonServer(std::string json_body) : m_body(std::move(json_body)) {
#ifdef _WIN32
      WSADATA wsa;
      WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
      m_listen_fd = ::socket(AF_INET, SOCK_STREAM, 0);
      int opt = 1;
#ifdef _WIN32
      setsockopt(m_listen_fd, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<char const*>(&opt),
                 sizeof(opt));
#else
      setsockopt(m_listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
      sockaddr_in addr{};
      addr.sin_family = AF_INET;
      addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
      addr.sin_port = htons(0);
      ::bind(m_listen_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
      ::listen(m_listen_fd, 8);

      sockaddr_in bound{};
#ifdef _WIN32
      int len = sizeof(bound);
#else
      socklen_t len = sizeof(bound);
#endif
      ::getsockname(m_listen_fd, reinterpret_cast<sockaddr*>(&bound), &len);
      m_port = ntohs(bound.sin_port);

      m_running.store(true);
      m_thread = std::thread([this]() { serve_loop(); });
   }

   ~LoopbackHttpJsonServer() { stop(); }

   int port() const { return m_port; }

   void stop() {
      if (!m_running.exchange(false)) {
         return;
      }
      if (m_listen_fd >= 0) {
#ifdef _WIN32
         closesocket(m_listen_fd);
#else
         ::shutdown(m_listen_fd, SHUT_RDWR);
         ::close(m_listen_fd);
#endif
         m_listen_fd = -1;
      }
      if (m_thread.joinable()) {
         m_thread.join();
      }
   }

  private:
   void serve_loop() {
      while (m_running.load()) {
         sockaddr_in caddr{};
#ifdef _WIN32
         int clen = sizeof(caddr);
         int cfd =
             static_cast<int>(::accept(m_listen_fd, reinterpret_cast<sockaddr*>(&caddr), &clen));
#else
         socklen_t clen = sizeof(caddr);
         int cfd = ::accept(m_listen_fd, reinterpret_cast<sockaddr*>(&caddr), &clen);
#endif
         if (cfd < 0) {
            break;
         }
         char buf[1024];
#ifdef _WIN32
         ::recv(cfd, buf, sizeof(buf), 0);
#else
         (void)::read(cfd, buf, sizeof(buf));
#endif
         std::string resp =
             "HTTP/1.1 200 OK\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: " +
             std::to_string(m_body.size()) +
             "\r\n"
             "Connection: close\r\n\r\n" +
             m_body;
#ifdef _WIN32
         ::send(cfd, resp.data(), static_cast<int>(resp.size()), 0);
         closesocket(cfd);
#else
         (void)::write(cfd, resp.data(), resp.size());
         ::close(cfd);
#endif
      }
   }

   std::string m_body;
   int m_listen_fd = -1;
   int m_port = 0;
   std::atomic<bool> m_running{false};
   std::thread m_thread;
};

TEST(VersionTest, CalSemVerAndBuildInfo) {
   EXPECT_FALSE(version().empty());
   EXPECT_TRUE(is_valid_calsemver(version()));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3a0"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3-alpha.0"));
   EXPECT_FALSE(is_valid_calsemver("2026.01.3"));
   EXPECT_FALSE(is_valid_calsemver("invalid"));
   EXPECT_FALSE(purpleair_api_target_version().empty());
   EXPECT_NE(build_info().find(version()), std::string::npos);
}

TEST(JsonUtilsTest, ParseAndSerializeRfc8259) {
   std::string raw = R"({
      "name": "sensor-1\nline2",
      "active": true,
      "disabled": false,
      "empty": null,
      "count": 42,
      "pm25": 12.75,
      "tags": ["outdoor", "pa-ii"]
   })";
   json::Value v = json::Value::parse(raw);
   EXPECT_TRUE(v.is_object());
   EXPECT_EQ(v.get("name").as_string(), "sensor-1\nline2");
   EXPECT_TRUE(v.get("active").as_bool());
   EXPECT_FALSE(v.get("disabled").as_bool(true));
   EXPECT_TRUE(v.get("empty").is_null());
   EXPECT_EQ(v.get("count").as_int(), 42);
   EXPECT_NEAR(v.get("pm25").as_double(), 12.75, 1e-6);
   EXPECT_EQ(v.get("tags").as_array().size(), 2u);

   std::string dumped = v.dump(2);
   json::Value reparsed = json::Value::parse(dumped);
   EXPECT_EQ(reparsed.get("count").as_int64(), 42);

   EXPECT_THROW(json::Value::parse("{invalid"), ConfigError);
}

TEST(DatatypesTest, SampleAndBatchNormalization) {
   Sample s_float =
       Sample::from_purpleair_field("pm2.5_atm", "pm2.5_atm", "131075", "FLOAT", "14.25");
   EXPECT_EQ(s_float.type_tag, TypeTag::Float64);
   EXPECT_NEAR(s_float.f64, 14.25, 1e-6);
   EXPECT_EQ(s_float.status, SampleStatus::Ok);

   Sample s_int = Sample::from_purpleair_field("humidity", "humidity", "131075", "INTEGER", "48");
   EXPECT_EQ(s_int.type_tag, TypeTag::Int64);
   EXPECT_EQ(s_int.i64, 48);

   Sample s_str =
       Sample::from_purpleair_field("sensor_name", "name", "131075", "STRING", "Backyard PA-II");
   EXPECT_EQ(s_str.type_tag, TypeTag::Str);
   EXPECT_EQ(s_str.str_val, "Backyard PA-II");

   Sample s_missing =
       Sample::from_purpleair_field("missing", "x", "131075", "NOSUCHINSTANCE", "No Such Instance");
   EXPECT_EQ(s_missing.status, SampleStatus::NoSuchInstance);

   Batch b;
   b.dut_name = "pa-sensor-01";
   b.dut_ip = "127.0.0.1";
   b.timestamp_ns = 1700000000000000000LL;
   b.samples = {s_float, s_int, s_str};

   std::string bj = b.to_json();
   Batch b2 = Batch::from_json(bj);
   EXPECT_EQ(b2.dut_name, "pa-sensor-01");
   ASSERT_EQ(b2.samples.size(), 3u);
   EXPECT_NEAR(b2.samples[0].f64, 14.25, 1e-6);
   EXPECT_EQ(b2.samples[1].i64, 48);
   EXPECT_EQ(b2.samples[2].str_val, "Backyard PA-II");
}

TEST(ConfigTest, TemplatesSchemaAndValidation) {
   for (std::string const& profile : {"minimal", "demo", "enterprise", "local"}) {
      std::string tpl = generate_template_config_json(profile);
      LoggerConfig cfg = LoggerConfig::from_json_string(tpl);
      ValidationReport rep = validate_config(cfg);
      EXPECT_TRUE(rep.valid) << "Profile failed validation: " << profile;
      EXPECT_GE(rep.enabled_duts, 1);
   }

   std::string schema = config_json_schema();
   json::Value sj = json::Value::parse(schema);
   EXPECT_TRUE(sj.is_object());
   EXPECT_TRUE(sj.contains("properties"));

   // Also verify array-style sinks parsing compatibility
   std::string arr_cfg_json = R"({
      "instance_name": "arr-test",
      "duts": [{
         "name": "s1",
         "dut_ip": "127.0.0.1",
         "purpleair": {"mode": "stub", "sensor_index": 131075},
         "metrics": [{"name": "pm2.5_atm", "field": "pm2.5_atm"}]
      }],
      "sinks": [
         {"type": "sqlite3", "enabled": true, "path": "./data/test.sqlite"}
      ]
   })";
   LoggerConfig arr_cfg = LoggerConfig::from_json_string(arr_cfg_json);
   EXPECT_TRUE(arr_cfg.sinks.sqlite.enabled);
   EXPECT_EQ(arr_cfg.sinks.sqlite.path, "./data/test.sqlite");
}

TEST(QueueAndSinksTest, SqliteCsvJsonlPrometheusAndInspect) {
   TempDir tmp("pa_dl_sinks");
   BoundedQueue<int> q(2);
   EXPECT_TRUE(q.try_push(10));
   EXPECT_TRUE(q.try_push(20));
   EXPECT_FALSE(q.try_push(30));
   EXPECT_EQ(q.pop_wait(std::chrono::milliseconds(50)).value_or(-1), 10);
   EXPECT_EQ(q.pop_wait(std::chrono::milliseconds(50)).value_or(-1), 20);
   q.close();
   EXPECT_FALSE(q.try_push(40));
   q.reopen();
   EXPECT_TRUE(q.try_push(50));

   LoggerConfig cfg;
   cfg.instance_name = "sink-test";
   cfg.sinks.sqlite.enabled = true;
   cfg.sinks.sqlite.path = (tmp.path() / "telemetry.sqlite3").string();
   cfg.sinks.csv.enabled = true;
   cfg.sinks.csv.directory = (tmp.path() / "csv").string();
   cfg.sinks.jsonl.enabled = true;
   cfg.sinks.jsonl.directory = (tmp.path() / "jsonl").string();
   cfg.sinks.prometheus.enabled = true;
   cfg.sinks.prometheus.bind_host = "127.0.0.1";
   cfg.sinks.prometheus.port = 0;

   Batch b;
   b.dut_name = "sensor-alpha";
   b.dut_ip = "192.168.1.20";
   b.timestamp_ns = 1700000001000000000LL;
   b.samples.push_back(
       Sample::from_purpleair_field("pm2.5_atm", "pm2.5_atm", "131075", "FLOAT", "11.8"));
   b.samples.push_back(
       Sample::from_purpleair_field("humidity", "humidity", "131075", "INTEGER", "52"));

   auto sinks = create_sinks(cfg.sinks);
   for (auto& s : sinks) {
      s->write_batch(b);
      s->flush();
   }

   auto rows = inspect_configured_sinks(cfg, 20, "sensor-alpha", "pm2.5_atm");
   ASSERT_FALSE(rows.empty());
   EXPECT_EQ(rows.front().dut_name, "sensor-alpha");
   EXPECT_EQ(rows.front().metric_name, "pm2.5_atm");
}

TEST(PurpleAirPollerTest, StubAndLiveLocalHttpEndpoint) {
   // 1. Stub poller
   DutConfig stub_dut;
   stub_dut.name = "stub-pa";
   stub_dut.dut_ip = "127.0.0.1";
   stub_dut.snmp.mode = "stub";
   stub_dut.snmp.port = 131075;
   MetricConfig m1;
   m1.name = "pm2.5_atm";
   m1.oid = "pm2.5_atm";
   stub_dut.metrics.push_back(m1);

   auto poller = create_poller(stub_dut);
   Batch b = poller->poll();
   ASSERT_EQ(b.samples.size(), 1u);
   EXPECT_EQ(b.samples[0].status, SampleStatus::Ok);
   EXPECT_GT(b.samples[0].f64, 0.0);

#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   // 2. Live PurpleAirPoller + PurpleAirAPI::PurpleAirLocalAPI over loopback HTTP
   std::string mock_local_json = R"({
      "SensorId": "aa:bb:cc:dd:ee:ff",
      "place": "lab",
      "current_temp_f": 72,
      "current_humidity": 44,
      "current_dewpoint_f": 49,
      "pressure": 1013.25,
      "pm2_5_atm": 9.4,
      "pm10_0_atm": 15.1
   })";
   LoopbackHttpJsonServer server(mock_local_json);

   DutConfig local_dut;
   local_dut.name = "local-lan-sensor";
   local_dut.dut_ip = "127.0.0.1";
   local_dut.snmp.mode = "local";
   local_dut.snmp.security_level = "local";
   local_dut.snmp.port = server.port();

   MetricConfig lm1;
   lm1.name = "pm2_5_atm";
   lm1.oid = "pm2_5_atm";
   lm1.operation = "local";
   MetricConfig lm2;
   lm2.name = "current_humidity";
   lm2.oid = "current_humidity";
   lm2.operation = "local";
   local_dut.metrics = {lm1, lm2};

   auto live_poller = create_poller(local_dut);
   Batch live_batch = live_poller->poll();
   ASSERT_EQ(live_batch.samples.size(), 2u);
   EXPECT_EQ(live_batch.samples[0].status, SampleStatus::Ok);
   EXPECT_NEAR(live_batch.samples[0].f64, 9.4, 1e-4);
   EXPECT_EQ(live_batch.samples[1].status, SampleStatus::Ok);
   EXPECT_EQ(live_batch.samples[1].i64, 44);
#endif
}

TEST(DataLoggerAndCliTest, EndToEndEngineAndCliSubcommands) {
   TempDir tmp("pa_dl_cli");
   std::string cfg_path = (tmp.path() / "config.json").string();

   auto r_init =
       CliRunner::execute({"init-config", "--template", "demo", "--output", cfg_path, "--json"});
   EXPECT_EQ(r_init.exit_code, 0);
   EXPECT_TRUE(std::filesystem::exists(cfg_path));

   // Point sinks into TempDir
   LoggerConfig cfg = LoggerConfig::from_json_file(cfg_path);
   cfg.sinks.sqlite.path = (tmp.path() / "cli.sqlite3").string();
   cfg.sinks.csv.directory = (tmp.path() / "csv").string();
   cfg.sinks.jsonl.directory = (tmp.path() / "jsonl").string();
   cfg.save_json_file(cfg_path, 2);

   auto r_val = CliRunner::execute({"validate", "-c", cfg_path, "--json"});
   EXPECT_EQ(r_val.exit_code, 0);
   EXPECT_TRUE(json::Value::parse(r_val.stdout_text).get("valid").as_bool());

   auto r_probe = CliRunner::execute({"probe", "-c", cfg_path, "--json"});
   EXPECT_EQ(r_probe.exit_code, 0);
   json::Value pj = json::Value::parse(r_probe.stdout_text);
   EXPECT_GE(pj.get("count").as_int(), 1);

   auto r_req = CliRunner::execute({"request", "-c", cfg_path, "--dut", "outdoor_patio_sensor",
                                    "--op", "get", "--oid", "pm2.5_atm", "--record", "--json"});
   EXPECT_EQ(r_req.exit_code, 0);
   json::Value rqj = json::Value::parse(r_req.stdout_text);
   EXPECT_EQ(rqj.get("samples").as_array().size(), 1u);

   auto r_set =
       CliRunner::execute({"set", "-c", cfg_path, "--dut", "outdoor_patio_sensor", "--oid",
                           "pm2.5_atm", "--type", "d", "--value", "21.5", "--record", "--json"});
   EXPECT_EQ(r_set.exit_code, 0);

   auto r_once = CliRunner::execute({"run", "-c", cfg_path, "--once", "--json"});
   EXPECT_EQ(r_once.exit_code, 0);

   auto r_insp = CliRunner::execute({"inspect", "-c", cfg_path, "--limit", "10", "--json"});
   EXPECT_EQ(r_insp.exit_code, 0);
   json::Value ij = json::Value::parse(r_insp.stdout_text);
   EXPECT_GE(ij.get("count").as_int(), 1);

   auto r_ver = CliRunner::execute({"version", "--json"});
   EXPECT_EQ(r_ver.exit_code, 0);
   EXPECT_EQ(json::Value::parse(r_ver.stdout_text).get("version").as_string(), version());

   auto r_schema = CliRunner::execute({"schema"});
   EXPECT_EQ(r_schema.exit_code, 0);
   EXPECT_FALSE(r_schema.stdout_text.empty());

   auto r_help = CliRunner::execute({"help"});
   EXPECT_EQ(r_help.exit_code, 0);
   EXPECT_NE(r_help.stdout_text.find("purpleair-data-logger"), std::string::npos);
}

} // namespace
} // namespace purpleair_data_logger

int main(int argc, char** argv) {
   ::testing::InitGoogleTest(&argc, argv);
   return RUN_ALL_TESTS();
}
