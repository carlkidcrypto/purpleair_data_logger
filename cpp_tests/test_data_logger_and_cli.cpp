#include <gtest/gtest.h>

#include "purpleair_data_logger/cli_runner.h"
#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/data_logger.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"
#include "test_common.h"

using namespace purpleair_data_logger;

TEST(DataLoggerLifecycleTest, StartStopRunIngestRecentAndErrors) {
   purpleair_dl_test::TempDir tmp("data_logger");

   LoggerConfig bad_cfg;
   bad_cfg.instance_name = "";
   EXPECT_THROW(DataLogger{bad_cfg}, ConfigError);

   LoggerConfig cfg = LoggerConfig::from_json_string(generate_template_config_json("minimal"));
   cfg.duts[0].poll_interval_ms = 60;
   cfg.max_poll_Cycles = 2;
   cfg.sinks.sqlite.enabled = true;
   cfg.sinks.sqlite.path = (tmp.path() / "dl.sqlite3").string();

   // Add a disabled DUT to exercise skip branch
   DutConfig dis_dut = cfg.duts[0];
   dis_dut.name = "disabled_sensor";
   dis_dut.enabled = false;
   cfg.duts.push_back(dis_dut);

   std::string cfg_file = (tmp.path() / "cfg.json").string();
   cfg.save_json_file(cfg_file, 2);

   DataLogger dl = DataLogger::from_json_file(cfg_file);
   EXPECT_EQ(dl.config().instance_name, cfg.instance_name);
   EXPECT_FALSE(dl.is_running());

   // Run for 120ms
   dl.run(120);
   dl.stop();
   EXPECT_FALSE(dl.is_running());

   // Start idempotency & ingest while running
   dl.start();
   dl.start();
   Batch custom_b = dl.probe_dut("");
   dl.ingest_batch(custom_b);
   dl.stop();

   // Ingest while stopped (>200 batches to test ring buffer cap)
   for (int i = 0; i < 205; ++i) {
      dl.ingest_batch(custom_b);
   }
   dl.ingest_batch_json(custom_b.to_json());
   dl.flush();

   EXPECT_EQ(dl.recent_batches(300).size(), 200u);
   EXPECT_FALSE(dl.recent_batches_json(5).empty());
   EXPECT_FALSE(dl.stats_json().empty());
   EXPECT_FALSE(dl.probe_dut_json("outdoor_patio_sensor").empty());
   EXPECT_THROW(dl.probe_dut("unknown_dut_xyz"), ConfigError);
}

TEST(CliRunnerCompleteTest, AllSubcommandsFlagsAndTextAndJsonModes) {
   purpleair_dl_test::TempDir tmp("cli_runner");
   std::string cfg_path = (tmp.path() / "config.json").string();

   // 1. Help & Version (text & json)
   EXPECT_EQ(CliRunner::execute({}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"--help"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"version"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"--version", "--json"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"schema"}).exit_code, 0);

   // 2. init-config (stdout, file text, file json)
   EXPECT_EQ(CliRunner::execute({"init-config", "--profile", "minimal"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"init-config", "--profile", "demo", "-o", cfg_path}).exit_code, 0);
   EXPECT_EQ(
       CliRunner::execute({"init-config", "--profile", "demo", "-o", cfg_path, "--json"}).exit_code,
       0);

   LoggerConfig cfg = LoggerConfig::from_json_file(cfg_path);
   cfg.duts[0].poll_interval_ms = 50;
   cfg.duts[1].enabled = false;
   cfg.sinks.sqlite.path = (tmp.path() / "cli.sqlite3").string();
   cfg.sinks.csv.directory = (tmp.path() / "csv").string();
   cfg.sinks.jsonl.directory = (tmp.path() / "jsonl").string();
   cfg.save_json_file(cfg_path, 2);

   // 3. validate (text & json, valid & invalid)
   EXPECT_EQ(CliRunner::execute({"validate", "-c", cfg_path}).exit_code, 0);
   EXPECT_EQ(
       CliRunner::execute({"validate", "--config-json", cfg.to_json_string(), "--json"}).exit_code,
       0);

   LoggerConfig warn_cfg = cfg;
   warn_cfg.duts[0].enabled = false;
   warn_cfg.sinks.sqlite.enabled = false;
   warn_cfg.sinks.csv.enabled = false;
   warn_cfg.sinks.jsonl.enabled = false;
   EXPECT_EQ(CliRunner::execute({"validate", "--config-json", warn_cfg.to_json_string()}).exit_code,
             0);

   LoggerConfig invalid_cfg = cfg;
   invalid_cfg.instance_name = "";
   EXPECT_EQ(
       CliRunner::execute({"validate", "--config-json", invalid_cfg.to_json_string()}).exit_code,
       2);

   // 4. probe (text & json, specific dut & all duts)
   EXPECT_EQ(CliRunner::execute({"probe", "-c", cfg_path}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"probe", "-c", cfg_path, "-d", "outdoor_patio_sensor", "--json"})
                 .exit_code,
             0);

   // 5. request (default oids, explicit oids, text & json, record)
   EXPECT_EQ(CliRunner::execute({"request", "-c", cfg_path}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"request", "-c", cfg_path, "--op", "walk", "--oid", "pm2.5_atm",
                                 "--max-repeaters", "10", "--record", "--json"})
                 .exit_code,
             0);

   // 6. set (valid with record, missing oid error)
   EXPECT_EQ(CliRunner::execute({"set", "-c", cfg_path, "--oid", "pm2.5_atm", "--type", "d",
                                 "--value", "15.2", "--record"})
                 .exit_code,
             0);
   EXPECT_EQ(CliRunner::execute({"set", "-c", cfg_path}).exit_code, 1);

   // 7. run (--once text & json, continuous with --cycles and --duration-ms in text & json)
   EXPECT_EQ(CliRunner::execute({"-c", cfg_path, "--once"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"run", "-c", cfg_path, "--once", "--json"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"run", "-c", cfg_path, "--cycles", "1", "--json"}).exit_code, 0);
   EXPECT_EQ(CliRunner::execute({"run", "-c", cfg_path, "--duration-ms", "120"}).exit_code, 0);

   // 8. inspect (text & json)
   EXPECT_EQ(CliRunner::execute({"inspect", "-c", cfg_path, "--limit", "5", "--metric", "pm2.5"})
                 .exit_code,
             0);
   EXPECT_EQ(CliRunner::execute({"inspect", "-c", cfg_path, "--json"}).exit_code, 0);

   // 9. Error handling branches (missing config, unknown flag, unsupported subcommand)
   EXPECT_EQ(CliRunner::execute({"validate"}).exit_code, 1);
   EXPECT_EQ(CliRunner::execute({"--unknown-flag"}).exit_code, 1);
   EXPECT_EQ(CliRunner::execute({"gui"}).exit_code, 1);
   EXPECT_EQ(CliRunner::run({"version"}), 0);
}
