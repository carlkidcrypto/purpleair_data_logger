#pragma once

#include <iosfwd>
#include <string>
#include <vector>

namespace purpleair_data_logger {

struct CliResult {
   int exit_code = 0;
   std::string stdout_text;
   std::string stderr_text;
};

class CliRunner {
  public:
   static int run(std::vector<std::string> const& args);
   static int run_streams(std::vector<std::string> const& args,
                          std::ostream& out,
                          std::ostream& err);
   static CliResult execute(std::vector<std::string> const& args);
   static std::string help_text();
};

} // namespace purpleair_data_logger
