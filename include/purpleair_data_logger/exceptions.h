#pragma once

#include <stdexcept>
#include <string>

namespace purpleair_data_logger {

class DataLoggerError : public std::runtime_error {
  public:
   explicit DataLoggerError(std::string const& message) : std::runtime_error(message) {}
};

class ConfigError : public DataLoggerError {
  public:
   explicit ConfigError(std::string const& message) : DataLoggerError(message) {}
};

class SinkError : public DataLoggerError {
  public:
   explicit SinkError(std::string const& message) : DataLoggerError(message) {}
};

class PollerError : public DataLoggerError {
  public:
   explicit PollerError(std::string const& message) : DataLoggerError(message) {}
};

} // namespace purpleair_data_logger
