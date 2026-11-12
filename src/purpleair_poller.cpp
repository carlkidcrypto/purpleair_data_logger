#include "purpleair_data_logger/purpleair_poller.h"

#include <chrono>
#include <cmath>
#include <sstream>
#include <unordered_map>

#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"

#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
#include "PurpleAirAPI.h"
#include "PurpleAirAPIError.h"
#include "PurpleAirAPIHelpers.h"
#include "PurpleAirLocalAPI.h"
#include "PurpleAirReadAPI.h"
#include "PurpleAirWriteAPI.h"
#endif

namespace purpleair_data_logger {

namespace {
int64_t now_ns() {
   auto now = std::chrono::system_clock::now().time_since_epoch();
   return std::chrono::duration_cast<std::chrono::nanoseconds>(now).count();
}

std::string join_fields(std::vector<std::string> const& fields, std::string const& fallback) {
   if (fields.empty()) {
      return fallback;
   }
   std::ostringstream oss;
   for (size_t i = 0; i < fields.size(); ++i) {
      if (i > 0) {
         oss << ",";
      }
      oss << fields[i];
   }
   return oss.str();
}

Sample json_value_to_sample(std::string const& metric_name,
                            std::string const& field_key,
                            std::string const& sensor_index,
                            json::Value const& val) {
   if (val.is_null()) {
      Sample s;
      s.metric_name = metric_name;
      s.oid = field_key;
      s.oid_index = sensor_index;
      s.snmp_type = "NULL";
      s.raw_value = "null";
      s.type_tag = TypeTag::Null;
      s.status = SampleStatus::Ok;
      return s;
   }
   if (val.is_int()) {
      int64_t iv = val.as_int64();
      return Sample::from_purpleair_field(metric_name, field_key, sensor_index, "INTEGER",
                                          std::to_string(iv));
   }
   if (val.is_number()) {
      std::ostringstream oss;
      oss.precision(6);
      oss << std::fixed << val.as_double();
      return Sample::from_purpleair_field(metric_name, field_key, sensor_index, "FLOAT", oss.str());
   }
   if (val.is_bool()) {
      return Sample::from_purpleair_field(metric_name, field_key, sensor_index, "INTEGER",
                                          val.as_bool() ? "1" : "0");
   }
   if (val.is_string()) {
      return Sample::from_purpleair_field(metric_name, field_key, sensor_index, "STRING",
                                          val.as_string());
   }
   return Sample::from_purpleair_field(metric_name, field_key, sensor_index, "STRING", val.dump());
}

std::vector<Sample> parse_purpleair_json_payload(
    std::string const& raw_json,
    std::string const& default_sensor_idx,
    std::vector<std::pair<std::string, std::string>> const& requested_metrics) {
   std::vector<Sample> out;
   json::Value root = json::Value::parse(raw_json);

   // Case 1: Local sensor array returned by PurpleAirLocalAPI::request_local_sensor_data()
   if (root.is_array() && !root.as_array().empty()) {
      root = root.as_array()[0];
   }

   if (!root.is_object()) {
      throw PollerError("Unexpected non-object JSON payload from PurpleAir API");
   }

   // Case 2: Cloud single sensor {"sensor": {...}}
   json::Value const& sensor_obj =
       root.contains("sensor") && root.get("sensor").is_object() ? root.get("sensor") : root;

   // Case 3: Cloud multiple sensors / history {"fields": [...], "data": [[...], ...]}
   if (root.contains("fields") && root.get("fields").is_array() && root.contains("data") &&
       root.get("data").is_array()) {
      auto const& fields_arr = root.get("fields").as_array();
      auto const& data_arr = root.get("data").as_array();
      std::vector<std::string> field_names;
      int sensor_idx_col = -1;
      for (size_t i = 0; i < fields_arr.size(); ++i) {
         std::string fn = fields_arr[i].as_string();
         field_names.push_back(fn);
         if (fn == "sensor_index") {
            sensor_idx_col = static_cast<int>(i);
         }
      }
      for (auto const& row_val : data_arr) {
         if (!row_val.is_array()) {
            continue;
         }
         auto const& row = row_val.as_array();
         std::string s_idx = default_sensor_idx;
         if (sensor_idx_col >= 0 && static_cast<size_t>(sensor_idx_col) < row.size()) {
            s_idx = row[static_cast<size_t>(sensor_idx_col)].is_int()
                        ? std::to_string(row[static_cast<size_t>(sensor_idx_col)].as_int64())
                        : row[static_cast<size_t>(sensor_idx_col)].as_string(default_sensor_idx);
         }
         for (size_t col = 0; col < row.size() && col < field_names.size(); ++col) {
            std::string const& fn = field_names[col];
            std::string mname = fn;
            for (auto const& req : requested_metrics) {
               if (req.second == fn || req.first == fn) {
                  mname = req.first;
                  break;
               }
            }
            out.push_back(json_value_to_sample(mname, fn, s_idx, row[col]));
         }
      }
      return out;
   }

   std::string s_idx = default_sensor_idx;
   if (sensor_obj.contains("sensor_index")) {
      auto const& sv = sensor_obj.get("sensor_index");
      s_idx = sv.is_int() ? std::to_string(sv.as_int64()) : sv.as_string(default_sensor_idx);
   } else if (sensor_obj.contains("SensorId")) {
      s_idx = sensor_obj.get("SensorId").as_string(default_sensor_idx);
   }

   if (!requested_metrics.empty()) {
      for (auto const& [mname, field_key] : requested_metrics) {
         if (sensor_obj.contains(field_key)) {
            out.push_back(json_value_to_sample(mname, field_key, s_idx, sensor_obj.get(field_key)));
         } else if (sensor_obj.contains(mname)) {
            out.push_back(json_value_to_sample(mname, field_key, s_idx, sensor_obj.get(mname)));
         }
      }
   }

   if (out.empty()) {
      for (auto const& [k, v] : sensor_obj.as_object()) {
         if (v.is_object() || v.is_array()) {
            continue;
         }
         out.push_back(json_value_to_sample(k, k, s_idx, v));
      }
   }

   return out;
}
} // namespace

StubSnmpPoller::StubSnmpPoller(DutConfig dut) : m_dut(std::move(dut)) {}

Sample StubSnmpPoller::make_stub_sample(std::string const& metric_name,
                                        std::string const& oid,
                                        uint64_t seq) const {
   std::string s_idx = std::to_string(m_dut.snmp.sensor_index > 0 ? m_dut.snmp.sensor_index : 53);

   if (metric_name.find("Descr") != std::string::npos ||
       metric_name.find("Name") != std::string::npos || metric_name == "name" || oid == "name" ||
       oid == "sysDescr.0" || oid == "1.3.6.1.2.1.1.1.0") {
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "STRING",
                                          "PurpleAir-PA-II-" + m_dut.name);
   }
   if (metric_name.find("UpTime") != std::string::npos || metric_name == "uptime" ||
       oid == "uptime" || oid == "sysUpTime.0" || oid == "1.3.6.1.2.1.1.3.0") {
      uint64_t ticks = 3600ULL + seq * 60ULL;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "INTEGER",
                                          std::to_string(ticks));
   }
   if (metric_name.find("pm2.5") != std::string::npos ||
       metric_name.find("pm2_5") != std::string::npos || oid.find("pm2.5") != std::string::npos) {
      double val = 12.4 + 3.2 * std::sin(static_cast<double>(seq) * 0.35);
      std::ostringstream oss;
      oss.precision(2);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("pm10") != std::string::npos || oid.find("pm10") != std::string::npos) {
      double val = 24.8 + 4.5 * std::sin(static_cast<double>(seq) * 0.25);
      std::ostringstream oss;
      oss.precision(2);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("pm1") != std::string::npos || oid.find("pm1") != std::string::npos) {
      double val = 7.1 + 1.8 * std::sin(static_cast<double>(seq) * 0.4);
      std::ostringstream oss;
      oss.precision(2);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("temp") != std::string::npos || oid.find("temp") != std::string::npos) {
      double val = 72.0 + 4.0 * std::sin(static_cast<double>(seq) * 0.2);
      std::ostringstream oss;
      oss.precision(1);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("humid") != std::string::npos || oid.find("humid") != std::string::npos) {
      double val = 45.0 + 6.0 * std::cos(static_cast<double>(seq) * 0.2);
      std::ostringstream oss;
      oss.precision(1);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("press") != std::string::npos || oid.find("press") != std::string::npos) {
      double val = 1013.25 + 1.5 * std::sin(static_cast<double>(seq) * 0.15);
      std::ostringstream oss;
      oss.precision(2);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("voc") != std::string::npos || oid.find("voc") != std::string::npos) {
      double val = 48.0 + 5.0 * std::sin(static_cast<double>(seq) * 0.3);
      std::ostringstream oss;
      oss.precision(1);
      oss << std::fixed << val;
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "FLOAT", oss.str());
   }
   if (metric_name.find("rssi") != std::string::npos || oid.find("rssi") != std::string::npos) {
      int64_t rssi = -62 + static_cast<int64_t>(seq % 5);
      return Sample::from_purpleair_field(metric_name, oid, s_idx, "INTEGER", std::to_string(rssi));
   }

   int64_t val = static_cast<int64_t>(
       50 + 25 * std::sin(static_cast<double>(seq) * 0.3 + static_cast<double>(oid.size())));
   return Sample::from_purpleair_field(metric_name, oid, s_idx, "INTEGER", std::to_string(val));
}

Batch StubSnmpPoller::poll() {
   ++m_counter;
   Batch b;
   b.dut_name = m_dut.name;
   b.dut_ip = m_dut.dut_ip;
   b.timestamp_ns = now_ns();
   for (auto const& m : m_dut.metrics) {
      b.samples.push_back(make_stub_sample(m.name, m.oid, m_counter));
   }
   return b;
}

std::vector<Sample> StubSnmpPoller::request(std::string const& operation,
                                            std::vector<std::string> const& oids,
                                            int max_repeaters) {
   (void)max_repeaters;
   ++m_counter;
   std::vector<Sample> out;
   for (auto const& oid : oids) {
      if (operation == "walk" || operation == "bulkwalk" || operation == "multiple") {
         for (int idx = 1; idx <= 3; ++idx) {
            Sample s = make_stub_sample(oid, oid, m_counter + static_cast<uint64_t>(idx));
            s.oid_index = std::to_string(m_dut.snmp.sensor_index + idx - 1);
            out.push_back(std::move(s));
         }
      } else {
         out.push_back(make_stub_sample(oid, oid, m_counter));
      }
   }
   return out;
}

std::vector<Sample> StubSnmpPoller::set_oid(
    std::vector<std::tuple<std::string, std::string, std::string>> const& oid_type_vals) {
   std::vector<Sample> out;
   std::string s_idx = std::to_string(m_dut.snmp.sensor_index > 0 ? m_dut.snmp.sensor_index : 53);
   for (auto const& [oid, tp, val] : oid_type_vals) {
      std::string stype = "STRING";
      if (tp == "i" || tp == "INTEGER") {
         stype = "INTEGER";
      } else if (tp == "d" || tp == "f" || tp == "FLOAT") {
         stype = "FLOAT";
      }
      out.push_back(Sample::from_purpleair_field(oid, oid, s_idx, stype, val));
   }
   return out;
}

struct PurpleAirPoller::Impl {
   explicit Impl(DutConfig d) : dut(std::move(d)) {}
   DutConfig dut;

#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   std::string execute_raw_query(std::string const& op, std::vector<std::string> const& fields) {
      std::string mode = dut.snmp.mode;
      bool is_local =
          (mode == "local" || op == "local" ||
           (!dut.dut_ip.empty() && dut.dut_ip != "api.purpleair.com" && mode != "cloud_single" &&
            mode != "cloud_multiple" && mode != "cloud_group"));

      if (is_local) {
         std::string target_host =
             !dut.snmp.ipv4_address.empty() ? dut.snmp.ipv4_address : dut.dut_ip;
         if (dut.snmp.port > 0 && dut.snmp.port != 80 &&
             target_host.find(':') == std::string::npos) {
            target_host += ":" + std::to_string(dut.snmp.port);
         }
         PurpleAirAPI::PurpleAirLocalAPI local_api({target_host});
         return local_api.request_local_sensor_data();
      }

      PurpleAirAPI::PurpleAirReadAPI read_api(dut.snmp.api_read_key);
      std::string field_csv = join_fields(fields, dut.snmp.fields);

      if (op == "multiple" || op == "walk" || op == "bulkwalk" || mode == "cloud_multiple") {
         return read_api.request_multiple_sensors_data(field_csv, dut.snmp.location_type,
                                                       dut.snmp.read_key, dut.snmp.show_only, "",
                                                       dut.snmp.max_age);
      }
      if (op == "history") {
         return read_api.request_sensor_history(dut.snmp.sensor_index, dut.snmp.read_key, 0, 0, 0,
                                                field_csv);
      }
      return read_api.request_sensor_data(dut.snmp.sensor_index, dut.snmp.read_key, field_csv);
   }
#endif
};

PurpleAirPoller::PurpleAirPoller(DutConfig dut) : m_impl(std::make_unique<Impl>(std::move(dut))) {}

PurpleAirPoller::~PurpleAirPoller() = default;

Batch PurpleAirPoller::poll() {
   Batch b;
   b.dut_name = m_impl->dut.name;
   b.dut_ip = m_impl->dut.dut_ip;
   b.timestamp_ns = now_ns();

#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   std::vector<std::string> field_list;
   std::vector<std::pair<std::string, std::string>> requested;
   std::string primary_op = "get";
   for (auto const& m : m_impl->dut.metrics) {
      field_list.push_back(m.oid);
      requested.emplace_back(m.name, m.oid);
      if (m.operation != "get") {
         primary_op = m.operation;
      }
   }

   try {
      std::string raw_json = m_impl->execute_raw_query(primary_op, field_list);
      std::string def_idx = std::to_string(m_impl->dut.snmp.sensor_index);
      b.samples = parse_purpleair_json_payload(raw_json, def_idx, requested);
   } catch (std::exception const& e) {
      std::string def_idx = std::to_string(m_impl->dut.snmp.sensor_index);
      for (auto const& m : m_impl->dut.metrics) {
         b.samples.push_back(
             Sample::from_purpleair_field(m.name, m.oid, def_idx, "ERROR", e.what()));
      }
   }
#else
   throw PollerError("PurpleAirPoller requires building with PURPLEAIR_DL_HAVE_PURPLEAIR_API=1");
#endif

   return b;
}

std::vector<Sample> PurpleAirPoller::request(std::string const& operation,
                                             std::vector<std::string> const& oids,
                                             int max_repeaters) {
   (void)max_repeaters;
#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   std::vector<std::pair<std::string, std::string>> requested;
   for (auto const& oid : oids) {
      requested.emplace_back(oid, oid);
   }
   try {
      std::string raw_json = m_impl->execute_raw_query(operation, oids);
      std::string def_idx = std::to_string(m_impl->dut.snmp.sensor_index);
      return parse_purpleair_json_payload(raw_json, def_idx, requested);
   } catch (std::exception const& e) {
      throw PollerError(std::string("purpleair_api ") + operation + " failed: " + e.what());
   }
#else
   (void)operation;
   (void)oids;
   throw PollerError("PurpleAirPoller requires building with PURPLEAIR_DL_HAVE_PURPLEAIR_API=1");
#endif
}

std::vector<Sample> PurpleAirPoller::set_oid(
    std::vector<std::tuple<std::string, std::string, std::string>> const& oid_type_vals) {
#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   std::vector<Sample> out;
   std::string s_idx = std::to_string(m_impl->dut.snmp.sensor_index);
   for (auto const& [oid, tp, val] : oid_type_vals) {
      if (oid == "post_create_member" && !m_impl->dut.snmp.api_write_key.empty()) {
         PurpleAirAPI::PurpleAirWriteAPI write_api(m_impl->dut.snmp.api_write_key);
         int target_sensor = std::stoi(val);
         std::string resp = write_api.post_create_member(target_sensor);
         out.push_back(Sample::from_purpleair_field(oid, oid, s_idx, "STRING", resp));
      } else {
         std::string stype = (tp == "i" || tp == "INTEGER") ? "INTEGER" : "STRING";
         out.push_back(Sample::from_purpleair_field(oid, oid, s_idx, stype, val));
      }
   }
   return out;
#else
   (void)oid_type_vals;
   throw PollerError("PurpleAirPoller requires building with PURPLEAIR_DL_HAVE_PURPLEAIR_API=1");
#endif
}

std::unique_ptr<ISnmpPoller> create_poller(DutConfig const& dut) {
   if (dut.snmp.mode != "stub") {
      return std::make_unique<PurpleAirPoller>(dut);
   }
   return std::make_unique<StubSnmpPoller>(dut);
}

} // namespace purpleair_data_logger
