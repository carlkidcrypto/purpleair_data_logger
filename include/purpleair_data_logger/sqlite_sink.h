#pragma once

#include <memory>
#include <string>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/sink.h"

namespace purpleair_data_logger {

class SqliteSink : public ISink {
  public:
   explicit SqliteSink(SqliteSinkConfig config);
   ~SqliteSink() override;

   std::string name() const override { return "sqlite"; }
   void write_batch(Batch const& batch) override;
   void flush() override;

  private:
   struct Impl;
   std::unique_ptr<Impl> m_impl;
};

} // namespace purpleair_data_logger
