#include "purpleair_data_logger/data_logger.h"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <thread>
#include <vector>

#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"
#include "purpleair_data_logger/purpleair_poller.h"
#include "purpleair_data_logger/queue.h"
#include "purpleair_data_logger/sink.h"

namespace purpleair_data_logger {

struct DataLogger::Impl {
   explicit Impl(LoggerConfig const& cfg_in)
       : cfg(cfg_in), queue(cfg_in.queue_capacity == 0 ? 4096 : cfg_in.queue_capacity) {
      ValidationReport r = validate_config(cfg);
      if (!r.valid) {
         throw ConfigError("Invalid LoggerConfig: " +
                           (r.errors.empty() ? "unknown error" : r.errors.front()));
      }
      sinks = create_sinks(cfg.sinks);
   }

   ~Impl() { stop(); }

   void record_recent(Batch const& b) {
      std::lock_guard<std::mutex> lock(recent_mutex);
      recent.push_back(b);
      while (recent.size() > 200) {
         recent.pop_front();
      }
   }

   void write_to_sinks(Batch const& b) {
      record_recent(b);
      bool any_ok = sinks.empty();
      for (auto& sink : sinks) {
         try {
            sink->write_batch(b);
            any_ok = true;
         } catch (...) {
            ++sink_errors;
         }
      }
      if (any_ok) {
         ++batches_written;
         samples_written += b.samples.size();
      }
   }

   void flush_sinks() {
      for (auto& sink : sinks) {
         try {
            sink->flush();
         } catch (...) {
            ++sink_errors;
         }
      }
   }

   void start() {
      std::lock_guard<std::mutex> lock(lifecycle_mutex);
      if (running.load()) {
         return;
      }
      stop_requested.store(false);
      running.store(true);
      queue.reopen();

      writer_thread = std::thread([this]() {
         while (!stop_requested.load() || queue.size() > 0) {
            auto item = queue.pop_wait(std::chrono::milliseconds(50));
            if (item.has_value()) {
               write_to_sinks(*item);
            }
         }
         flush_sinks();
      });

      for (auto const& dut : cfg.duts) {
         if (!dut.enabled) {
            continue;
         }
         poller_threads.emplace_back([this, dut]() {
            auto poller = create_poller(dut);
            int cycles = 0;
            while (!stop_requested.load()) {
               auto t0 = std::chrono::steady_clock::now();
               try {
                  Batch b = poller->poll();
                  ++batches_polled;
                  bool has_err = false;
                  for (auto const& s : b.samples) {
                     if (s.status != SampleStatus::Ok) {
                        has_err = true;
                     }
                  }
                  if (has_err) {
                     ++poll_errors;
                  }
                  if (queue.push_wait(std::move(b), std::chrono::milliseconds(100))) {
                     ++batches_enqueued;
                  } else {
                     ++batches_dropped;
                  }
               } catch (...) {
                  ++poll_errors;
               }
               ++cycles;
               if (cfg.max_poll_Cycles > 0 && cycles >= cfg.max_poll_Cycles) {
                  break;
               }
               auto elapsed = std::chrono::steady_clock::now() - t0;
               auto target = std::chrono::milliseconds(dut.poll_interval_ms);
               if (elapsed < target) {
                  std::unique_lock<std::mutex> slock(sleep_mutex);
                  sleep_cv.wait_for(slock, target - elapsed,
                                    [this]() { return stop_requested.load(); });
               }
            }
         });
      }
   }

   void stop() {
      std::lock_guard<std::mutex> lock(lifecycle_mutex);
      if (!running.load() && poller_threads.empty() && !writer_thread.joinable()) {
         return;
      }
      stop_requested.store(true);
      sleep_cv.notify_all();
      for (auto& t : poller_threads) {
         if (t.joinable()) {
            t.join();
         }
      }
      poller_threads.clear();
      queue.close();
      if (writer_thread.joinable()) {
         writer_thread.join();
      }
      running.store(false);
   }

   DutConfig const& find_dut(std::string const& dut_name) const {
      if (cfg.duts.empty()) {
         throw ConfigError("No sensor targets configured");
      }
      if (dut_name.empty()) {
         return cfg.duts.front();
      }
      for (auto const& d : cfg.duts) {
         if (d.name == dut_name) {
            return d;
         }
      }
      throw ConfigError("Unknown sensor target name: " + dut_name);
   }

   LoggerConfig cfg;
   BoundedQueue<Batch> queue;
   std::vector<std::unique_ptr<ISink>> sinks;

   std::mutex lifecycle_mutex;
   std::mutex sleep_mutex;
   std::condition_variable sleep_cv;
   std::vector<std::thread> poller_threads;
   std::thread writer_thread;

   std::atomic<bool> running{false};
   std::atomic<bool> stop_requested{false};
   std::atomic<uint64_t> batches_polled{0};
   std::atomic<uint64_t> batches_enqueued{0};
   std::atomic<uint64_t> batches_dropped{0};
   std::atomic<uint64_t> batches_written{0};
   std::atomic<uint64_t> samples_written{0};
   std::atomic<uint64_t> poll_errors{0};
   std::atomic<uint64_t> sink_errors{0};

   mutable std::mutex recent_mutex;
   std::deque<Batch> recent;
};

DataLogger::DataLogger(LoggerConfig const& config) : m_impl(std::make_shared<Impl>(config)) {}

DataLogger DataLogger::from_json_file(std::string const& path) {
   return DataLogger(LoggerConfig::from_json_file(path));
}

DataLogger DataLogger::from_json_string(std::string const& json_str) {
   return DataLogger(LoggerConfig::from_json_string(json_str));
}

DataLogger::~DataLogger() = default;

void DataLogger::start() { m_impl->start(); }

void DataLogger::stop() { m_impl->stop(); }

void DataLogger::run(int duration_ms) {
   start();
   if (duration_ms > 0) {
      std::this_thread::sleep_for(std::chrono::milliseconds(duration_ms));
      stop();
   } else {
      while (is_running()) {
         std::this_thread::sleep_for(std::chrono::milliseconds(50));
      }
   }
}

std::vector<Batch> DataLogger::run_once() {
   std::vector<Batch> out;
   for (auto const& dut : m_impl->cfg.duts) {
      if (!dut.enabled) {
         continue;
      }
      auto poller = create_poller(dut);
      Batch b = poller->poll();
      ++m_impl->batches_polled;
      ++m_impl->batches_enqueued;
      m_impl->write_to_sinks(b);
      out.push_back(std::move(b));
   }
   m_impl->flush_sinks();
   return out;
}

void DataLogger::ingest_batch(Batch const& batch) {
   ++m_impl->batches_polled;
   if (m_impl->running.load()) {
      if (m_impl->queue.push_wait(batch, std::chrono::milliseconds(200))) {
         ++m_impl->batches_enqueued;
      } else {
         ++m_impl->batches_dropped;
      }
   } else {
      ++m_impl->batches_enqueued;
      m_impl->write_to_sinks(batch);
   }
}

void DataLogger::ingest_batch_json(std::string const& batch_json) {
   ingest_batch(Batch::from_json(batch_json));
}

void DataLogger::flush() { m_impl->flush_sinks(); }

bool DataLogger::is_running() const { return m_impl->running.load(); }

LoggerStats DataLogger::stats() const {
   LoggerStats s;
   s.batches_polled = m_impl->batches_polled.load();
   s.batches_enqueued = m_impl->batches_enqueued.load();
   s.batches_dropped = m_impl->batches_dropped.load();
   s.batches_written = m_impl->batches_written.load();
   s.samples_written = m_impl->samples_written.load();
   s.poll_errors = m_impl->poll_errors.load();
   s.sink_errors = m_impl->sink_errors.load();
   s.queue_depth = m_impl->queue.size();
   s.running = m_impl->running.load();
   return s;
}

std::string DataLogger::stats_json() const { return stats().to_json(); }

std::vector<Batch> DataLogger::recent_batches(size_t max_items) const {
   std::lock_guard<std::mutex> lock(m_impl->recent_mutex);
   std::vector<Batch> out;
   size_t count = std::min(max_items, m_impl->recent.size());
   auto it = m_impl->recent.end() - static_cast<std::ptrdiff_t>(count);
   for (; it != m_impl->recent.end(); ++it) {
      out.push_back(*it);
   }
   return out;
}

std::string DataLogger::recent_batches_json(size_t max_items) const {
   auto batches = recent_batches(max_items);
   json::Value arr = json::Value::make_array();
   for (auto const& b : batches) {
      arr.push_back(json::Value::parse(b.to_json()));
   }
   return arr.dump();
}

LoggerConfig DataLogger::config() const { return m_impl->cfg; }

Batch DataLogger::probe_dut(std::string const& dut_name) {
   DutConfig const& dut = m_impl->find_dut(dut_name);
   auto poller = create_poller(dut);
   return poller->poll();
}

std::string DataLogger::probe_dut_json(std::string const& dut_name) {
   return probe_dut(dut_name).to_json();
}

std::string DataLogger::request_json(std::string const& dut_name,
                                     std::string const& operation,
                                     std::vector<std::string> const& oids,
                                     int max_repeaters) {
   DutConfig const& dut = m_impl->find_dut(dut_name);
   auto t0 = std::chrono::steady_clock::now();
   auto poller = create_poller(dut);
   auto samples = poller->request(operation, oids, max_repeaters);
   double latency_ms =
       std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();

   Batch b;
   b.dut_name = dut.name;
   b.dut_ip = dut.dut_ip;
   b.timestamp_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::system_clock::now().time_since_epoch())
                        .count();
   b.samples = samples;

   json::Value root = json::Value::make_object();
   root.set("dut_name", json::Value(dut.name));
   root.set("dut_ip", json::Value(dut.dut_ip));
   root.set("operation", json::Value(operation));
   root.set("latency_ms", json::Value(latency_ms));
   root.set("batch", json::Value::parse(b.to_json()));
   json::Value sarr = json::Value::make_array();
   for (auto const& s : samples) {
      sarr.push_back(json::Value::parse(s.to_json()));
   }
   root.set("samples", std::move(sarr));
   return root.dump();
}

std::string DataLogger::set_json(std::string const& dut_name,
                                 std::string const& oid,
                                 std::string const& snmp_type,
                                 std::string const& value) {
   DutConfig const& dut = m_impl->find_dut(dut_name);
   auto t0 = std::chrono::steady_clock::now();
   auto poller = create_poller(dut);
   auto samples = poller->set_oid({std::make_tuple(oid, snmp_type, value)});
   double latency_ms =
       std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();

   Batch b;
   b.dut_name = dut.name;
   b.dut_ip = dut.dut_ip;
   b.timestamp_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
                        std::chrono::system_clock::now().time_since_epoch())
                        .count();
   b.samples = samples;

   json::Value root = json::Value::make_object();
   root.set("dut_name", json::Value(dut.name));
   root.set("dut_ip", json::Value(dut.dut_ip));
   root.set("operation", json::Value("set"));
   root.set("latency_ms", json::Value(latency_ms));
   root.set("batch", json::Value::parse(b.to_json()));
   json::Value sarr = json::Value::make_array();
   for (auto const& s : samples) {
      sarr.push_back(json::Value::parse(s.to_json()));
   }
   root.set("samples", std::move(sarr));
   return root.dump();
}

} // namespace purpleair_data_logger
