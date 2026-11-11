#include "purpleair_data_logger/datatypes.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>

#include "purpleair_data_logger/json_utils.h"

namespace purpleair_data_logger {

namespace {
std::string to_upper_ascii(std::string s) {
   for (char& c : s) {
      c = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
   }
   return s;
}

std::string trim_numeric_prefix(std::string const& raw) {
   size_t start = 0;
   while (start < raw.size() && std::isspace(static_cast<unsigned char>(raw[start]))) {
      ++start;
   }
   size_t pos = start;
   if (pos < raw.size() && (raw[pos] == '-' || raw[pos] == '+')) {
      ++pos;
   }
   bool has_digit = false;
   while (pos < raw.size() &&
          (std::isdigit(static_cast<unsigned char>(raw[pos])) || raw[pos] == '.')) {
      if (std::isdigit(static_cast<unsigned char>(raw[pos]))) {
         has_digit = true;
      }
      ++pos;
   }
   return has_digit ? raw.substr(start, pos - start) : "";
}
} // namespace

Sample Sample::from_purpleair_field(std::string const& metric_name,
                                    std::string const& field_key,
                                    std::string const& sensor_index,
                                    std::string const& value_type,
                                    std::string const& raw_value) {
   return from_ezsnmp_result(metric_name, field_key, sensor_index, value_type, raw_value);
}

Sample Sample::from_ezsnmp_result(std::string const& metric_name,
                                  std::string const& oid,
                                  std::string const& oid_index,
                                  std::string const& snmp_type,
                                  std::string const& raw_value) {
   Sample s;
   s.metric_name = metric_name;
   s.oid = oid;
   s.oid_index = oid_index;
   s.snmp_type = snmp_type;
   s.raw_value = raw_value;
   s.str_val = raw_value;

   std::string upper_type = to_upper_ascii(snmp_type);
   std::string upper_val = to_upper_ascii(raw_value);

   if (upper_type.find("NOSUCHINSTANCE") != std::string::npos ||
       upper_type.find("NOSUCHOBJECT") != std::string::npos ||
       upper_type.find("ENDOFMIBVIEW") != std::string::npos ||
       upper_val.find("NO SUCH INSTANCE") != std::string::npos ||
       upper_val.find("NO SUCH OBJECT") != std::string::npos) {
      s.status = SampleStatus::NoSuchInstance;
      s.type_tag = TypeTag::Null;
      return s;
   }

   if (upper_type == "ERROR" || upper_type == "TIMEOUT") {
      s.status = (upper_type == "TIMEOUT") ? SampleStatus::Timeout : SampleStatus::Error;
      s.type_tag = TypeTag::Str;
      return s;
   }

   if (upper_type == "INTEGER" || upper_type == "INT" || upper_type == "INT64" ||
       upper_type == "COUNTER32" || upper_type == "COUNTER64" || upper_type == "GAUGE32" ||
       upper_type == "UNSIGNED32" || upper_type == "TIMETICKS") {
      if (upper_type == "TIMETICKS") {
         size_t lp = raw_value.find('(');
         size_t rp = raw_value.find(')', lp == std::string::npos ? 0 : lp);
         if (lp != std::string::npos && rp != std::string::npos && rp > lp + 1) {
            std::string ticks = raw_value.substr(lp + 1, rp - lp - 1);
            s.i64 = std::strtoll(ticks.c_str(), nullptr, 10);
            s.f64 = static_cast<double>(s.i64);
            s.type_tag = TypeTag::Int64;
            return s;
         }
      }
      std::string num_str = trim_numeric_prefix(raw_value);
      if (!num_str.empty()) {
         s.i64 = std::strtoll(num_str.c_str(), nullptr, 10);
         s.f64 = static_cast<double>(s.i64);
         s.type_tag = TypeTag::Int64;
         return s;
      }
   }

   if (upper_type == "OPAQUE" || upper_type == "FLOAT" || upper_type == "DOUBLE" ||
       upper_type == "REAL") {
      std::string num_str = trim_numeric_prefix(raw_value);
      if (!num_str.empty()) {
         s.f64 = std::strtod(num_str.c_str(), nullptr);
         s.i64 = static_cast<int64_t>(s.f64);
         s.type_tag = TypeTag::Float64;
         return s;
      }
   }

   std::string candidate = trim_numeric_prefix(raw_value);
   if (!candidate.empty() && candidate.size() == raw_value.size()) {
      if (candidate.find('.') != std::string::npos) {
         s.f64 = std::strtod(candidate.c_str(), nullptr);
         s.i64 = static_cast<int64_t>(s.f64);
         s.type_tag = TypeTag::Float64;
      } else {
         s.i64 = std::strtoll(candidate.c_str(), nullptr, 10);
         s.f64 = static_cast<double>(s.i64);
         s.type_tag = TypeTag::Int64;
      }
      return s;
   }

   s.type_tag = TypeTag::Str;
   return s;
}

Sample Sample::from_json(std::string const& metric_name, std::string const& result_json) {
   json::Value v = json::Value::parse(result_json);
   std::string mname = v.get("metric_name").as_string(metric_name);
   std::string oid = v.get("oid").as_string(v.get("field").as_string());
   std::string idx =
       v.get("oid_index").as_string(v.get("index").as_string(v.get("sensor_index").as_string()));
   std::string stype = v.get("snmp_type").as_string(v.get("type").as_string("STRING"));
   std::string val = v.get("raw_value").as_string(v.get("value").as_string());
   Sample s = from_ezsnmp_result(mname, oid, idx, stype, val);
   if (v.contains("type_tag")) {
      s.type_tag = static_cast<TypeTag>(v.get("type_tag").as_int(static_cast<int>(s.type_tag)));
   }
   if (v.contains("i64")) {
      s.i64 = v.get("i64").as_int64(s.i64);
   }
   if (v.contains("f64")) {
      s.f64 = v.get("f64").as_double(s.f64);
   }
   if (v.contains("str_val")) {
      s.str_val = v.get("str_val").as_string(s.str_val);
   }
   if (v.contains("status")) {
      s.status = static_cast<SampleStatus>(v.get("status").as_int(static_cast<int>(s.status)));
   }
   return s;
}

std::string Sample::to_json() const {
   json::Value obj = json::Value::make_object();
   obj.set("metric_name", json::Value(metric_name));
   obj.set("oid", json::Value(oid));
   obj.set("oid_index", json::Value(oid_index));
   obj.set("snmp_type", json::Value(snmp_type));
   obj.set("raw_value", json::Value(raw_value));
   obj.set("type_tag", json::Value(static_cast<int>(type_tag)));
   std::string tname = "null";
   if (type_tag == TypeTag::Int64) {
      tname = "i64";
   } else if (type_tag == TypeTag::Float64) {
      tname = "f64";
   } else if (type_tag == TypeTag::Str) {
      tname = "str";
   }
   obj.set("type_name", json::Value(tname));
   obj.set("i64", json::Value(i64));
   obj.set("f64", json::Value(f64));
   obj.set("str_val", json::Value(str_val));
   obj.set("status", json::Value(static_cast<int>(status)));
   return obj.dump();
}

std::string Batch::to_json() const {
   json::Value obj = json::Value::make_object();
   obj.set("dut_name", json::Value(dut_name));
   obj.set("dut_ip", json::Value(dut_ip));
   obj.set("timestamp_ns", json::Value(timestamp_ns));
   obj.set("ts_unix_ns", json::Value(timestamp_ns));
   json::Value arr = json::Value::make_array();
   for (auto const& s : samples) {
      arr.push_back(json::Value::parse(s.to_json()));
   }
   obj.set("samples", std::move(arr));
   return obj.dump();
}

Batch Batch::from_json(std::string const& batch_json) {
   json::Value v = json::Value::parse(batch_json);
   Batch b;
   b.dut_name = v.get("dut_name").as_string();
   b.dut_ip = v.get("dut_ip").as_string();
   b.timestamp_ns = v.get("timestamp_ns").as_int64(v.get("ts_unix_ns").as_int64());
   json::Value const& sarr = v.get("samples");
   if (sarr.is_array()) {
      for (auto const& item : sarr.as_array()) {
         b.samples.push_back(Sample::from_json("", item.dump()));
      }
   }
   return b;
}

std::string LoggerStats::to_json() const {
   json::Value obj = json::Value::make_object();
   obj.set("batches_polled", json::Value(static_cast<int64_t>(batches_polled)));
   obj.set("batches_enqueued", json::Value(static_cast<int64_t>(batches_enqueued)));
   obj.set("batches_dropped", json::Value(static_cast<int64_t>(batches_dropped)));
   obj.set("batches_written", json::Value(static_cast<int64_t>(batches_written)));
   obj.set("samples_written", json::Value(static_cast<int64_t>(samples_written)));
   obj.set("cycles_completed", json::Value(static_cast<int64_t>(batches_polled)));
   obj.set("processed_batches", json::Value(static_cast<int64_t>(batches_written)));
   obj.set("processed_samples", json::Value(static_cast<int64_t>(samples_written)));
   obj.set("dropped_batches", json::Value(static_cast<int64_t>(batches_dropped)));
   obj.set("poll_errors", json::Value(static_cast<int64_t>(poll_errors)));
   obj.set("sink_errors", json::Value(static_cast<int64_t>(sink_errors)));
   obj.set("queue_depth", json::Value(static_cast<int64_t>(queue_depth)));
   obj.set("running", json::Value(running));
   return obj.dump();
}

std::string ValidationReport::to_json() const {
   json::Value obj = json::Value::make_object();
   obj.set("valid", json::Value(valid));
   json::Value errs = json::Value::make_array();
   for (auto const& e : errors) {
      errs.push_back(json::Value(e));
   }
   obj.set("errors", std::move(errs));
   json::Value warns = json::Value::make_array();
   for (auto const& w : warnings) {
      warns.push_back(json::Value(w));
   }
   obj.set("warnings", std::move(warns));
   obj.set("enabled_duts", json::Value(enabled_duts));
   obj.set("total_metrics", json::Value(total_metrics));
   obj.set("enabled_sinks", json::Value(enabled_sinks));
   return obj.dump();
}

std::string SinkRow::to_json() const {
   json::Value obj = json::Value::make_object();
   obj.set("sink_type", json::Value(sink_type));
   obj.set("timestamp_ns", json::Value(timestamp_ns));
   obj.set("ts_unix_ns", json::Value(timestamp_ns));
   obj.set("dut_name", json::Value(dut_name));
   obj.set("dut_ip", json::Value(dut_ip));
   obj.set("metric_name", json::Value(metric_name));
   obj.set("oid", json::Value(oid));
   obj.set("oid_index", json::Value(oid_index));
   obj.set("snmp_type", json::Value(snmp_type));
   obj.set("value", json::Value(value));
   obj.set("str_val", json::Value(value));
   obj.set("raw_value", json::Value(raw_value));
   obj.set("status", json::Value(status));
   return obj.dump();
}

} // namespace purpleair_data_logger
