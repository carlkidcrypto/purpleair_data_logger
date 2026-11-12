#include <csignal>
#include <string>
#include <vector>

#include "purpleair_data_logger/cli_runner.h"

int main(int argc, char** argv) {
   std::vector<std::string> args;
   args.reserve(static_cast<size_t>(argc > 1 ? argc - 1 : 0));
   for (int i = 1; i < argc; ++i) {
      args.emplace_back(argv[i]);
   }
   return purpleair_data_logger::CliRunner::run(args);
}
