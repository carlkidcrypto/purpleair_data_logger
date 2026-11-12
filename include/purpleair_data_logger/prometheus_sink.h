#pragma once

#include <memory>
#include <string>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/sink.h"

namespace purpleair_data_logger {

class PrometheusSink : public ISink {
  public:
   explicit PrometheusSink(PrometheusSinkConfig config);
   ~PrometheusSink() override;

   std::string name() const override { return "prometheus"; }
   void write_batch(Batch const& batch) override;
   void flush() override;

   std::string render_metrics() const;
   int bound_port() const;

  private:
   struct Impl;
   std::unique_ptr<Impl> m_impl;
};

} // namespace purpleair_data_logger
