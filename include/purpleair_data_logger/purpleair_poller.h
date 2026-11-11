#pragma once

#include <cstdint>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/datatypes.h"

namespace purpleair_data_logger {

/**
 * @brief Interface for polling a PurpleAir sensor target (cloud or local) via purpleair_api.
 */
class ISnmpPoller {
  public:
   virtual ~ISnmpPoller() = default;
   virtual Batch poll() = 0;
   virtual std::vector<Sample> request(std::string const& operation,
                                       std::vector<std::string> const& oids,
                                       int max_repeaters = 25) = 0;
   virtual std::vector<Sample> set_oid(
       std::vector<std::tuple<std::string, std::string, std::string>> const& oid_type_vals) = 0;
};

using IPurpleAirPoller = ISnmpPoller;

/**
 * @brief Deterministic synthetic PurpleAir poller for offline testing, demos, and CI validation.
 */
class StubSnmpPoller : public ISnmpPoller {
  public:
   explicit StubSnmpPoller(DutConfig dut);
   Batch poll() override;
   std::vector<Sample> request(std::string const& operation,
                               std::vector<std::string> const& oids,
                               int max_repeaters = 25) override;
   std::vector<Sample> set_oid(std::vector<std::tuple<std::string, std::string, std::string>> const&
                                   oid_type_vals) override;

  private:
   Sample make_stub_sample(std::string const& metric_name,
                           std::string const& oid,
                           uint64_t seq) const;

   DutConfig m_dut;
   uint64_t m_counter = 0;
};

using StubPurpleAirPoller = StubSnmpPoller;

/**
 * @brief Live PurpleAir poller backed directly by purpleair_api's C++17 classes
 * (PurpleAirAPI, PurpleAirReadAPI, PurpleAirWriteAPI, PurpleAirLocalAPI).
 */
class PurpleAirPoller : public ISnmpPoller {
  public:
   explicit PurpleAirPoller(DutConfig dut);
   ~PurpleAirPoller() override;

   Batch poll() override;
   std::vector<Sample> request(std::string const& operation,
                               std::vector<std::string> const& oids,
                               int max_repeaters = 25) override;
   std::vector<Sample> set_oid(std::vector<std::tuple<std::string, std::string, std::string>> const&
                                   oid_type_vals) override;

  private:
   struct Impl;
   std::unique_ptr<Impl> m_impl;
};

using EzSnmpPoller = PurpleAirPoller;

std::unique_ptr<ISnmpPoller> create_poller(DutConfig const& dut);

} // namespace purpleair_data_logger
