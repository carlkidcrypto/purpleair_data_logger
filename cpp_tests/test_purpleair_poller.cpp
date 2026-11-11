#include <gtest/gtest.h>

#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/purpleair_poller.h"
#include "test_common.h"

using namespace purpleair_data_logger;

TEST(StubPollerTest, AllMetricPatternsRequestAndSetOid) {
   DutConfig dut;
   dut.name = "stub-patio";
   dut.dut_ip = "127.0.0.1";
   dut.snmp.mode = "stub";
   dut.snmp.sensor_index = 108;
   dut.metrics = {
       {"name", "name", "get", 25},
       {"uptime", "uptime", "get", 25},
       {"pm2.5_atm", "pm2.5_atm", "get", 25},
       {"pm10.0_atm", "pm10.0_atm", "get", 25},
       {"pm1.0_atm", "pm1.0_atm", "get", 25},
       {"temperature", "temperature", "get", 25},
       {"humidity", "humidity", "get", 25},
       {"pressure", "pressure", "get", 25},
       {"voc", "voc", "get", 25},
       {"rssi", "rssi", "get", 25},
       {"custom_oid", "1.3.6.1.99", "get", 25},
   };

   auto poller = create_poller(dut);
   Batch b = poller->poll();
   ASSERT_EQ(b.samples.size(), 11u);

   auto single_res = poller->request("get", {"pm2.5_atm", "humidity"}, 10);
   EXPECT_EQ(single_res.size(), 2u);

   auto walk_res = poller->request("walk", {"pm2.5_atm"}, 10);
   EXPECT_EQ(walk_res.size(), 3u);

   auto set_res = poller->set_oid({
       {"field_s", "s", "hello"},
       {"field_i", "i", "42"},
       {"field_f", "f", "3.14"},
   });
   ASSERT_EQ(set_res.size(), 3u);
   EXPECT_EQ(set_res[0].type_tag, TypeTag::Str);
   EXPECT_EQ(set_res[1].type_tag, TypeTag::Int64);
   EXPECT_EQ(set_res[2].type_tag, TypeTag::Float64);
}

#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
TEST(PurpleAirLivePollerTest, LocalJsonVariantsAndCloudErrorHandling) {
   // 1. Local sensor returning single object with null, bool, int, float, string, nested obj
   std::string json_single = R"({
      "sensor": {
         "sensor_index": 184291,
         "name": "Lab PA-II",
         "private": false,
         "active": true,
         "humidity": 48,
         "pm2.5_atm": 11.25,
         "empty_field": null,
         "stats": {"pm2.5": 11.25}
      }
   })";
   purpleair_dl_test::LoopbackHttpJsonServer srv1(json_single);

   DutConfig d1;
   d1.name = "local-1";
   d1.dut_ip = "127.0.0.1";
   d1.snmp.mode = "local";
   d1.snmp.port = srv1.port();
   d1.snmp.sensor_index = 184291;
   d1.metrics = {
       {"name", "name", "local", 25},      {"private", "private", "local", 25},
       {"active", "active", "local", 25},  {"humidity", "humidity", "local", 25},
       {"pm25", "pm2.5_atm", "local", 25}, {"empty_field", "empty_field", "local", 25},
       {"stats", "stats", "local", 25},
   };

   auto p1 = create_poller(d1);
   Batch b1 = p1->poll();
   EXPECT_EQ(b1.samples.size(), 7u);

   // Request with unmapped metric name so fallback loop over all object keys executes
   auto fallback_samples = p1->request("local", {"nonexistent_metric_xyz"}, 10);
   EXPECT_GE(fallback_samples.size(), 5u);

   // 2. Tabular {"fields": [...], "data": [[...]]} payload over local mock server
   std::string json_tabular = R"({
      "fields": ["sensor_index", "pm2.5_atm", "humidity", "name"],
      "data": [
         "ignore_non_array_row",
         [184291, 9.8, 51, "SensorA"],
         ["184292", 14.2, 49, "SensorB"]
      ]
   })";
   purpleair_dl_test::LoopbackHttpJsonServer srv2(json_tabular);
   DutConfig d2 = d1;
   d2.snmp.port = srv2.port();
   auto p2 = create_poller(d2);
   Batch b2 = p2->poll();
   EXPECT_EQ(b2.samples.size(), 8u);

   // 3. Non-object JSON payload triggers PollerError caught in poll() and thrown in request()
   purpleair_dl_test::LoopbackHttpJsonServer srv3("12345");
   DutConfig d3 = d1;
   d3.snmp.port = srv3.port();
   auto p3 = create_poller(d3);
   Batch b3 = p3->poll();
   ASSERT_FALSE(b3.samples.empty());
   EXPECT_EQ(b3.samples[0].status, SampleStatus::Error);
   EXPECT_THROW(p3->request("local", {"pm2.5_atm"}, 10), PollerError);

   // 4. Cloud single, multiple, history, and set_oid paths (empty/invalid key error handling)
   DutConfig d_cloud;
   d_cloud.name = "cloud-dut";
   d_cloud.dut_ip = "api.purpleair.com";
   d_cloud.snmp.mode = "cloud_single";
   d_cloud.snmp.sensor_index = 53;
   d_cloud.metrics = {{"pm2.5_atm", "pm2.5_atm", "get", 25}};
   auto p_cloud = create_poller(d_cloud);
   Batch b_cloud = p_cloud->poll();
   EXPECT_EQ(b_cloud.samples.size(), 1u);

   EXPECT_THROW(p_cloud->request("multiple", {}, 10), PollerError);
   EXPECT_THROW(p_cloud->request("history", {"pm2.5_atm"}, 10), PollerError);

   auto set_local = p_cloud->set_oid({{"custom_field", "i", "10"}});
   ASSERT_EQ(set_local.size(), 1u);
   EXPECT_EQ(set_local[0].i64, 10);

   d_cloud.snmp.api_write_key = "invalid-key";
   auto p_write = create_poller(d_cloud);
   EXPECT_THROW(p_write->set_oid({{"post_create_member", "i", "53"}}), std::exception);
}
#endif
