#include <gtest/gtest.h>

#include <cstdlib>
#include <filesystem>
#include <string>

using namespace std::string_literals;

TEST(MainBinaryExecutionTest, InvokeCompiledCliBinary) {
   std::filesystem::path bin = std::filesystem::current_path() / "purpleair-data-logger";
#ifdef _WIN32
   bin += ".exe";
#endif
   if (!std::filesystem::exists(bin)) {
      bin = std::filesystem::current_path().parent_path() / "purpleair-data-logger";
#ifdef _WIN32
      bin += ".exe";
#endif
   }
   if (std::filesystem::exists(bin)) {
      std::string cmd = "\"" + bin.string() + "\" version --json";
      int rc = std::system(cmd.c_str());
      EXPECT_EQ(rc, 0);
   }
}
