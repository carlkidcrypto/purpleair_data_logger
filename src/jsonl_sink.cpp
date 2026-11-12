#include "purpleair_data_logger/jsonl_sink.h"

#include <cctype>
#include <filesystem>

#include "purpleair_data_logger/exceptions.h"

namespace purpleair_data_logger {

JsonlSink::JsonlSink(JsonlSinkConfig config) : m_cfg(std::move(config)) {
   if (m_cfg.enabled) {
      std::error_code ec;
      std::filesystem::create_directories(m_cfg.directory, ec);
      if (ec) {
         throw SinkError("Failed to create JSONL directory '" + m_cfg.directory +
                         "': " + ec.message());
      }
   }
}

JsonlSink::~JsonlSink() {
   try {
      flush();
   } catch (...) {
   }
}

std::string JsonlSink::sanitize_filename(std::string const& val) {
   std::string out;
   out.reserve(val.size());
   for (unsigned char c : val) {
      if (std::isalnum(c) || c == '_' || c == '-' || c == '.') {
         out.push_back(static_cast<char>(c));
      } else {
         out.push_back('_');
      }
   }
   return out.empty() ? "sensor" : out;
}

std::ofstream& JsonlSink::get_or_open_stream(std::string const& dut_name) {
   auto it = m_streams.find(dut_name);
   if (it != m_streams.end() && it->second.is_open()) {
      return it->second;
   }
   std::filesystem::path file_path =
       std::filesystem::path(m_cfg.directory) / (sanitize_filename(dut_name) + ".jsonl");
   std::ofstream ofs(file_path, std::ios::out | std::ios::app);
   if (!ofs) {
      throw SinkError("Failed to open JSONL sink file: " + file_path.string());
   }
   auto [inserted_it, _] = m_streams.emplace(dut_name, std::move(ofs));
   return inserted_it->second;
}

void JsonlSink::write_batch(Batch const& batch) {
   if (!m_cfg.enabled) {
      return;
   }
   std::lock_guard<std::mutex> lock(m_mutex);
   std::ofstream& ofs = get_or_open_stream(batch.dut_name);
   ofs << batch.to_json() << "\n";
   ++m_batches_since_flush;
   if (m_cfg.flush_every_n_batches <= 1 || m_batches_since_flush >= m_cfg.flush_every_n_batches) {
      ofs.flush();
      m_batches_since_flush = 0;
   }
}

void JsonlSink::flush() {
   std::lock_guard<std::mutex> lock(m_mutex);
   for (auto& kv : m_streams) {
      if (kv.second.is_open()) {
         kv.second.flush();
      }
   }
   m_batches_since_flush = 0;
}

} // namespace purpleair_data_logger
