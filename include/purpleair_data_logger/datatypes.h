#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace purpleair_data_logger {

enum class TypeTag {
   Null = 0,
   Int64 = 1,
   Float64 = 2,
   Str = 3,
};

enum class SampleStatus {
   Ok = 0,
   Timeout = 1,
   NoSuchInstance = 2,
   Error = 3,
};

struct Sample {
   std::string metric_name;
   std::string oid;
   std::string oid_index;
   std::string snmp_type;
   std::string raw_value;
   TypeTag type_tag = TypeTag::Null;
   int64_t i64 = 0;
   double f64 = 0.0;
   std::string str_val;
   SampleStatus status = SampleStatus::Ok;

   Sample() = default;

   static Sample from_purpleair_field(std::string const& metric_name,
                                      std::string const& field_key,
                                      std::string const& sensor_index,
                                      std::string const& value_type,
                                      std::string const& raw_value);

   static Sample from_ezsnmp_result(std::string const& metric_name,
                                    std::string const& oid,
                                    std::string const& oid_index,
                                    std::string const& snmp_type,
                                    std::string const& raw_value);

   static Sample from_json(std::string const& metric_name, std::string const& result_json);

   std::string to_json() const;
};

struct Batch {
   std::string dut_name;
   std::string dut_ip;
   int64_t timestamp_ns = 0;
   std::vector<Sample> samples;

   Batch() = default;
   std::string to_json() const;
   static Batch from_json(std::string const& batch_json);
};

struct LoggerStats {
   uint64_t batches_polled = 0;
   uint64_t batches_enqueued = 0;
   uint64_t batches_dropped = 0;
   uint64_t batches_written = 0;
   uint64_t samples_written = 0;
   uint64_t poll_errors = 0;
   uint64_t sink_errors = 0;
   uint64_t queue_depth = 0;
   bool running = false;

   std::string to_json() const;
};

struct ValidationReport {
   bool valid = true;
   std::vector<std::string> errors;
   std::vector<std::string> warnings;
   int enabled_duts = 0;
   int total_metrics = 0;
   int enabled_sinks = 0;

   std::string to_json() const;
};

struct SinkRow {
   std::string sink_type;
   int64_t timestamp_ns = 0;
   std::string dut_name;
   std::string dut_ip;
   std::string metric_name;
   std::string oid;
   std::string oid_index;
   std::string snmp_type;
   std::string value;
   std::string raw_value;
   int status = 0;

   std::string to_json() const;
};

} // namespace purpleair_data_logger
