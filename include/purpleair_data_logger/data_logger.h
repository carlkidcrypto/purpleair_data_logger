#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/datatypes.h"

namespace purpleair_data_logger {

/**
 * @brief High-throughput multi-sensor data logger engine with SWIG-friendly PIMPL handle.
 */
class DataLogger {
  public:
   explicit DataLogger(LoggerConfig const& config);
   static DataLogger from_json_file(std::string const& path);
   static DataLogger from_json_string(std::string const& json_str);

   DataLogger(DataLogger const&) = default;
   DataLogger& operator=(DataLogger const&) = default;
   DataLogger(DataLogger&&) noexcept = default;
   DataLogger& operator=(DataLogger&&) noexcept = default;
   ~DataLogger();

   void start();
   void stop();
   void run(int duration_ms = 0);
   std::vector<Batch> run_once();
   void ingest_batch(Batch const& batch);
   void ingest_batch_json(std::string const& batch_json);
   void flush();

   bool is_running() const;
   LoggerStats stats() const;
   std::string stats_json() const;
   std::vector<Batch> recent_batches(size_t max_items = 20) const;
   std::string recent_batches_json(size_t max_items = 20) const;
   LoggerConfig config() const;

   Batch probe_dut(std::string const& dut_name = "");
   std::string probe_dut_json(std::string const& dut_name = "");

   std::string request_json(std::string const& dut_name,
                            std::string const& operation,
                            std::vector<std::string> const& oids,
                            int max_repeaters = 25);

   std::string set_json(std::string const& dut_name,
                        std::string const& oid,
                        std::string const& snmp_type,
                        std::string const& value);

  private:
   struct Impl;
   std::shared_ptr<Impl> m_impl;
};

} // namespace purpleair_data_logger
