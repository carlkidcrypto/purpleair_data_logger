#include <gtest/gtest.h>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/datatypes.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"
#include "purpleair_data_logger/version.h"
#include "test_common.h"

using namespace purpleair_data_logger;

TEST(VersionCompleteTest, AllCalSemVerBranches) {
   EXPECT_EQ(version(), "2026.11.3a0");
   EXPECT_EQ(purpleair_api_target_version(), "2026.11.11a2");
   EXPECT_NE(build_info().find("purpleair_data_logger"), std::string::npos);

   EXPECT_TRUE(is_valid_calsemver("2026.11.3"));
   EXPECT_TRUE(is_valid_calsemver("v2026.11.3"));
   EXPECT_TRUE(is_valid_calsemver("V2026.11.3.1"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3a0"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3b1"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3rc2"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3.1a0"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3-0"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3-alpha.0"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3-beta.1"));
   EXPECT_TRUE(is_valid_calsemver("2026.11.3-rc.2"));

   EXPECT_FALSE(is_valid_calsemver(""));
   EXPECT_FALSE(is_valid_calsemver("2026.11"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3.1.2"));
   EXPECT_FALSE(is_valid_calsemver("202.11.3"));
   EXPECT_FALSE(is_valid_calsemver("02026.11.3"));
   EXPECT_FALSE(is_valid_calsemver("2019.11.3"));
   EXPECT_FALSE(is_valid_calsemver("2200.11.3"));
   EXPECT_FALSE(is_valid_calsemver("2026.01.3"));
   EXPECT_FALSE(is_valid_calsemver("2026.13.3"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.03"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.32"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3.01"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3a0-alpha.0"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3x0"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3a"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3-unknown"));
   EXPECT_FALSE(is_valid_calsemver("2026.11.3-"));
}

TEST(DatatypesCompleteTest, SampleBatchStatsReportAndRowConversions) {
   Sample s_tt = Sample::from_ezsnmp_result("uptime", "1.3.6.1", "0", "TIMETICKS",
                                            "Timeticks: (123456) 0:20");
   EXPECT_EQ(s_tt.type_tag, TypeTag::Int64);
   EXPECT_EQ(s_tt.i64, 123456);

   Sample s_int = Sample::from_ezsnmp_result("rssi", "rssi", "53", "INTEGER", "-62 dBm");
   EXPECT_EQ(s_int.type_tag, TypeTag::Int64);
   EXPECT_EQ(s_int.i64, -62);

   Sample s_flt = Sample::from_ezsnmp_result("pm", "pm2.5", "53", "FLOAT", "+12.50 ug/m3");
   EXPECT_EQ(s_flt.type_tag, TypeTag::Float64);
   EXPECT_NEAR(s_flt.f64, 12.5, 1e-6);

   Sample s_auto_f = Sample::from_ezsnmp_result("pm", "pm2.5", "53", "UNKNOWN", "45.75");
   EXPECT_EQ(s_auto_f.type_tag, TypeTag::Float64);

   Sample s_auto_i = Sample::from_ezsnmp_result("cnt", "cnt", "53", "UNKNOWN", "88");
   EXPECT_EQ(s_auto_i.type_tag, TypeTag::Int64);

   Sample s_err = Sample::from_ezsnmp_result("err", "oid", "0", "ERROR", "failed");
   EXPECT_EQ(s_err.status, SampleStatus::Error);

   Sample s_tmo = Sample::from_ezsnmp_result("tmo", "oid", "0", "TIMEOUT", "timed out");
   EXPECT_EQ(s_tmo.status, SampleStatus::Timeout);

   Sample s_nosuch = Sample::from_ezsnmp_result("ns", "oid", "0", "STRING", "No Such Object");
   EXPECT_EQ(s_nosuch.status, SampleStatus::NoSuchInstance);
   EXPECT_EQ(s_nosuch.type_tag, TypeTag::Null);
   EXPECT_NE(s_nosuch.to_json().find("\"type_name\":\"null\""), std::string::npos);

   std::string custom_s_json = R"({
      "metric_name": "m1",
      "oid": "o1",
      "oid_index": "53",
      "snmp_type": "FLOAT",
      "raw_value": "9.5",
      "type_tag": 2,
      "i64": 9,
      "f64": 9.5,
      "str_val": "9.5",
      "status": 0
   })";
   Sample s_parsed = Sample::from_json("fallback", custom_s_json);
   EXPECT_EQ(s_parsed.metric_name, "m1");
   EXPECT_NEAR(s_parsed.f64, 9.5, 1e-6);

   LoggerStats st;
   st.batches_polled = 5;
   st.batches_written = 4;
   EXPECT_NE(st.to_json().find("\"batches_polled\":5"), std::string::npos);

   ValidationReport vr;
   vr.valid = false;
   vr.errors.push_back("e1");
   vr.warnings.push_back("w1");
   EXPECT_NE(vr.to_json().find("\"e1\""), std::string::npos);

   SinkRow sr;
   sr.sink_type = "sqlite";
   sr.dut_name = "d1";
   sr.metric_name = "m1";
   sr.value = "10";
   EXPECT_NE(sr.to_json().find("\"sink_type\":\"sqlite\""), std::string::npos);
}

TEST(ConfigCompleteTest, AllProfilesSinksAndValidationErrors) {
   for (std::string const& prof : {"", "minimal", "demo", "enterprise", "local", "snmpv3"}) {
      std::string j = generate_template_config_json(prof);
      ValidationReport r = validate_config_json(j);
      EXPECT_TRUE(r.valid) << "Profile failed: " << prof;
   }

   EXPECT_THROW(LoggerConfig::from_json_string("[1, 2, 3]"), ConfigError);
   EXPECT_THROW(LoggerConfig::from_json_file("/nonexistent/path/config.json"), ConfigError);

   ValidationReport bad_json = validate_config_json("{bad json");
   EXPECT_FALSE(bad_json.valid);
   ValidationReport bad_file = validate_config_file("/nonexistent/path/config.json");
   EXPECT_FALSE(bad_file.valid);

   // Array-style sinks covering all 5 sink types + non-object element
   std::string arr_sinks = R"({
      "logger": {"instance_name": "arr", "queue_capacity": 100, "max_poll_cycles": 2},
      "duts": [
         "ignore_non_object",
         {
            "name": "d1",
            "host": "127.0.0.1",
            "enabled": false,
            "poll_interval_ms": 100,
            "snmp": {"mode": "stub", "version": "3", "port": 161, "security_level": "authPriv",
                     "security_username": "u", "auth_passphrase": "12345678",
                     "priv_passphrase": "12345678"},
            "metrics": ["ignore_non_object", {"name": "m1", "oid": "o1", "operation": "get"}]
         }
      ],
      "sinks": [
         "ignore",
         {"type": "sqlite", "enabled": false, "path": "a.db"},
         {"type": "csv", "enabled": false, "dir": "c"},
         {"type": "jsonl", "enabled": false, "dir": "j"},
         {"type": "psql", "enabled": false, "conninfo": "pg"},
         {"type": "prometheus", "enabled": false, "port": 9102}
      ],
      "gui": {"frontend": "web", "theme": "light"}
   })";
   LoggerConfig cfg_arr = LoggerConfig::from_json_string(arr_sinks);
   ValidationReport rep_warn = validate_config(cfg_arr);
   EXPECT_TRUE(rep_warn.valid);
   EXPECT_EQ(rep_warn.warnings.size(), 2u);

   // Trigger all validation error branches
   LoggerConfig bad;
   bad.instance_name = "";
   bad.queue_capacity = 0;
   ValidationReport r_empty = validate_config(bad);
   EXPECT_FALSE(r_empty.valid);

   DutConfig d1;
   d1.name = "";
   d1.dut_ip = "";
   d1.poll_interval_ms = 10;
   d1.snmp.mode = "invalid_mode";
   d1.snmp.version = "invalid_ver";
   d1.snmp.port = 70000;

   DutConfig d2;
   d2.name = "dup";
   d2.snmp.version = "3";
   d2.snmp.security_level = "authPriv";
   d2.snmp.security_username = "";
   d2.snmp.auth_passphrase = "short";
   d2.snmp.priv_passphrase = "short";
   d2.metrics.push_back({"", "", "invalid_op", 10});

   DutConfig d3;
   d3.name = "dup";
   d3.snmp.version = "1";
   d3.metrics.push_back({"m", "o", "bulkwalk", 10});

   bad.duts = {d1, d2, d3};
   bad.sinks.sqlite.enabled = true;
   bad.sinks.sqlite.path = "";
   bad.sinks.csv.enabled = true;
   bad.sinks.csv.directory = "";
   bad.sinks.jsonl.enabled = true;
   bad.sinks.jsonl.directory = "";
   bad.sinks.psql.enabled = true;
   bad.sinks.psql.conninfo = "";
   bad.sinks.prometheus.enabled = true;
   bad.sinks.prometheus.port = 99999;
   bad.gui.frontend = "invalid_gui";

   ValidationReport r_all = validate_config(bad);
   EXPECT_FALSE(r_all.valid);
   EXPECT_GE(r_all.errors.size(), 15u);

   purpleair_dl_test::TempDir tmp("cfg_save");
   std::string valid_file = (tmp.path() / "sub" / "cfg.json").string();
   LoggerConfig good = LoggerConfig::from_json_string(generate_template_config_json("minimal"));
   good.save_json_file(valid_file, 2);
   EXPECT_TRUE(validate_config_file(valid_file).valid);
}
