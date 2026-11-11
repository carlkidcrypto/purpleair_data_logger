#pragma once

#include <string>

namespace purpleair_data_logger {

/**
 * @brief Return the current purpleair_data_logger CalSemVer string (e.g. "2026.11.3a0").
 *
 * CalSemVer format: YYYY.M.D (stable) or YYYY.M.DaN / YYYY.M.DbN / YYYY.M.DrcN (pre-release)
 * with no zero-padding on month or day segments.
 */
std::string version();

/**
 * @brief Return the minimum supported purpleair_api CalSemVer release string.
 */
std::string purpleair_api_target_version();

/**
 * @brief Return build and feature flags (C++ standard, purpleair_api, SQLite3, libpq).
 */
std::string build_info();

/**
 * @brief Validate whether a version string conforms to CalSemVer (YYYY.M.D[...]).
 */
bool is_valid_calsemver(std::string const& ver);

} // namespace purpleair_data_logger
