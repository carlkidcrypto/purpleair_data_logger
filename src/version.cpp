#include "purpleair_data_logger/version.h"

#include <cctype>
#include <sstream>
#include <vector>

namespace purpleair_data_logger {

namespace {
constexpr char const* PROJECT_VERSION_STRING = "2026.11.3a0";
constexpr char const* PURPLEAIR_API_TARGET_VERSION_STRING = "2026.11.3";

bool is_non_zero_padded_digits(std::string const& s) {
   if (s.empty()) {
      return false;
   }
   for (char c : s) {
      if (!std::isdigit(static_cast<unsigned char>(c))) {
         return false;
      }
   }
   if (s.size() > 1 && s[0] == '0') {
      return false;
   }
   return true;
}

bool is_all_digits(std::string const& s) {
   if (s.empty()) {
      return false;
   }
   for (char c : s) {
      if (!std::isdigit(static_cast<unsigned char>(c))) {
         return false;
      }
   }
   return true;
}
} // namespace

std::string version() { return PROJECT_VERSION_STRING; }

std::string purpleair_api_target_version() { return PURPLEAIR_API_TARGET_VERSION_STRING; }

std::string build_info() {
   std::string info = "purpleair_data_logger ";
   info += version();
   info += " (C++17; purpleair_api=";
#ifdef PURPLEAIR_DL_HAVE_PURPLEAIR_API
   info += "enabled; target>=";
   info += purpleair_api_target_version();
#else
   info += "stub-only";
#endif
   info += "; sqlite3=";
#ifdef PURPLEAIR_DL_HAVE_SQLITE3
   info += "enabled";
#else
   info += "disabled";
#endif
   info += "; libpq=";
#ifdef PURPLEAIR_DL_HAVE_LIBPQ
   info += "enabled";
#else
   info += "disabled";
#endif
   info += ")";
   return info;
}

bool is_valid_calsemver(std::string const& raw_ver) {
   if (raw_ver.empty()) {
      return false;
   }
   std::string s = raw_ver;
   if (s[0] == 'v' || s[0] == 'V') {
      s.erase(0, 1);
   }

   std::string suffix;
   size_t hyphen_pos = s.find('-');
   if (hyphen_pos != std::string::npos) {
      suffix = s.substr(hyphen_pos);
      s = s.substr(0, hyphen_pos);
   }

   std::vector<std::string> parts;
   std::stringstream ss(s);
   std::string item;
   while (std::getline(ss, item, '.')) {
      parts.push_back(item);
   }
   if (parts.size() < 3 || parts.size() > 4) {
      return false;
   }

   std::string const& year_str = parts[0];
   if (year_str.size() != 4 || !is_non_zero_padded_digits(year_str)) {
      return false;
   }
   int year = std::stoi(year_str);
   if (year < 2020 || year > 2199) {
      return false;
   }

   std::string const& month_str = parts[1];
   if (!is_non_zero_padded_digits(month_str)) {
      return false;
   }
   int month = std::stoi(month_str);
   if (month < 1 || month > 12) {
      return false;
   }

   std::string day_part = parts[2];
   std::string pep440_pre;
   if (parts.size() == 3) {
      size_t alpha_pos = std::string::npos;
      for (size_t i = 0; i < day_part.size(); ++i) {
         if (!std::isdigit(static_cast<unsigned char>(day_part[i]))) {
            alpha_pos = i;
            break;
         }
      }
      if (alpha_pos != std::string::npos) {
         pep440_pre = day_part.substr(alpha_pos);
         day_part = day_part.substr(0, alpha_pos);
      }
   }

   if (!is_non_zero_padded_digits(day_part)) {
      return false;
   }
   int day = std::stoi(day_part);
   if (day < 1 || day > 31) {
      return false;
   }

   if (parts.size() == 4) {
      std::string patch_part = parts[3];
      size_t alpha_pos = std::string::npos;
      for (size_t i = 0; i < patch_part.size(); ++i) {
         if (!std::isdigit(static_cast<unsigned char>(patch_part[i]))) {
            alpha_pos = i;
            break;
         }
      }
      if (alpha_pos != std::string::npos) {
         pep440_pre = patch_part.substr(alpha_pos);
         patch_part = patch_part.substr(0, alpha_pos);
      }
      if (!is_non_zero_padded_digits(patch_part)) {
         return false;
      }
   }

   if (!pep440_pre.empty()) {
      if (!suffix.empty()) {
         return false;
      }
      if (pep440_pre.rfind("rc", 0) == 0) {
         return is_all_digits(pep440_pre.substr(2));
      }
      if (pep440_pre[0] == 'a' || pep440_pre[0] == 'b') {
         return is_all_digits(pep440_pre.substr(1));
      }
      return false;
   }

   if (!suffix.empty()) {
      if (suffix.rfind("-alpha.", 0) == 0) {
         return is_all_digits(suffix.substr(7));
      }
      if (suffix.rfind("-beta.", 0) == 0) {
         return is_all_digits(suffix.substr(6));
      }
      if (suffix.rfind("-rc.", 0) == 0) {
         return is_all_digits(suffix.substr(4));
      }
      if (suffix.size() > 1 && suffix[0] == '-') {
         return is_all_digits(suffix.substr(1));
      }
      return false;
   }

   return true;
}

} // namespace purpleair_data_logger
