#include <gtest/gtest.h>

#include <fstream>

#include "purpleair_data_logger/csv_sink.h"
#include "purpleair_data_logger/jsonl_sink.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/sqlite_sink.h"
#include "test_common.h"

using namespace purpleair_data_logger;

TEST(SinkInspectorTest, InspectSqliteJsonlAndCsvWithFiltersAndQuotes) {
   purpleair_dl_test::TempDir tmp("inspector");

   Batch b1;
   b1.dut_name = "alpha-sensor";
   b1.dut_ip = "192.168.1.10";
   b1.timestamp_ns = 1700000100000LL;
   b1.samples.push_back(Sample::from_purpleair_field("pm2.5_atm", "pm2.5", "53", "FLOAT", "12.3"));
   b1.samples.push_back(
       Sample::from_purpleair_field("note", "note", "53", "STRING", "val, \"quoted\""));

   Batch b2;
   b2.dut_name = "beta-sensor";
   b2.dut_ip = "192.168.1.11";
   b2.timestamp_ns = 1700000200000LL;
   b2.samples.push_back(Sample::from_purpleair_field("humidity", "hum", "54", "INTEGER", "55"));

   LoggerConfig cfg;
   cfg.sinks.sqlite.enabled = true;
   cfg.sinks.sqlite.path = (tmp.path() / "data.sqlite3").string();
   cfg.sinks.jsonl.enabled = true;
   cfg.sinks.jsonl.directory = (tmp.path() / "jsonl").string();
   cfg.sinks.csv.enabled = true;
   cfg.sinks.csv.directory = (tmp.path() / "csv").string();

   auto sinks = create_sinks(cfg.sinks);
   ASSERT_EQ(sinks.size(), 3u);
   for (auto& s : sinks) {
      s->write_batch(b1);
      s->write_batch(b2);
      s->flush();
   }

   // Add corrupt line & non-matching extension files to JSONL and CSV dirs
   {
      std::ofstream bad_jl(tmp.path() / "jsonl" / "extra.jsonl", std::ios::app);
      bad_jl << "\n{corrupt_json\n";
      std::ofstream ignored_txt(tmp.path() / "jsonl" / "ignore.txt");
      ignored_txt << "ignore";

      std::ofstream short_csv(tmp.path() / "csv" / "short.csv");
      short_csv << "header\n1,2,3\r\n";
      std::ofstream ignored_csv_txt(tmp.path() / "csv" / "ignore.txt");
      ignored_csv_txt << "ignore";
   }

   // 1. Inspect across all 3 sinks (limit <= 0 defaults to 100)
   auto all_rows = inspect_configured_sinks(cfg, 0, "", "");
   EXPECT_GE(all_rows.size(), 6u);

   // 2. Inspect with dut_filter and metric_filter
   auto filtered = inspect_configured_sinks(cfg, 10, "alpha-sensor", "note");
   ASSERT_FALSE(filtered.empty());
   EXPECT_EQ(filtered.front().dut_name, "alpha-sensor");
   EXPECT_EQ(filtered.front().metric_name, "note");

   // 3. Inspect JSONL only
   LoggerConfig jl_only = cfg;
   jl_only.sinks.sqlite.enabled = false;
   jl_only.sinks.csv.enabled = false;
   auto jl_rows = inspect_configured_sinks(jl_only, 1, "alpha-sensor", "");
   ASSERT_EQ(jl_rows.size(), 1u);
   EXPECT_EQ(jl_rows.front().sink_type, "jsonl");

   // 4. Inspect CSV only (including quoted CSV fields)
   LoggerConfig csv_only = cfg;
   csv_only.sinks.sqlite.enabled = false;
   csv_only.sinks.jsonl.enabled = false;
   auto csv_rows = inspect_configured_sinks(csv_only, 10, "alpha-sensor", "note");
   ASSERT_EQ(csv_rows.size(), 1u);
   EXPECT_EQ(csv_rows.front().sink_type, "csv");
   EXPECT_EQ(csv_rows.front().value, "val, \"quoted\"");
}
