#pragma once

#include <fstream>
#include <mutex>
#include <string>
#include <unordered_map>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/sink.h"

namespace purpleair_data_logger {

class JsonlSink : public ISink {
  public:
   explicit JsonlSink(JsonlSinkConfig config);
   ~JsonlSink() override;

   std::string name() const override { return "jsonl"; }
   void write_batch(Batch const& batch) override;
   void flush() override;

  private:
   std::ofstream& get_or_open_stream(std::string const& dut_name);
   static std::string sanitize_filename(std::string const& val);

   JsonlSinkConfig m_cfg;
   std::mutex m_mutex;
   std::unordered_map<std::string, std::ofstream> m_streams;
   int m_batches_since_flush = 0;
};

} // namespace purpleair_data_logger
