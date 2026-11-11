#pragma once

#include <memory>
#include <string>
#include <vector>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/datatypes.h"

namespace purpleair_data_logger {

class ISink {
  public:
   virtual ~ISink() = default;
   virtual std::string name() const = 0;
   virtual void write_batch(Batch const& batch) = 0;
   virtual void flush() = 0;
};

std::vector<std::unique_ptr<ISink>> create_sinks(SinksConfig const& cfg);

std::vector<SinkRow> inspect_configured_sinks(LoggerConfig const& cfg,
                                              int limit = 100,
                                              std::string const& dut_filter = "",
                                              std::string const& metric_filter = "");

} // namespace purpleair_data_logger
