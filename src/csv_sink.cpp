#include "purpleair_data_logger/csv_sink.h"

#include <cctype>
#include <filesystem>

#include "purpleair_data_logger/exceptions.h"

namespace purpleair_data_logger {

CsvSink::CsvSink(CsvSinkConfig config) : m_cfg(std::move(config)) {
   if (m_cfg.enabled) {
      std::error_code ec;
      std::filesystem::create_directories(m_cfg.directory, ec);
      if (ec) {
         throw SinkError("Failed to create CSV directory '" + m_cfg.directory +
                         "': " + ec.message());
      }
   }
}

CsvSink::~CsvSink() {
   try {
      flush();
   } catch (...) {
   }
}

std::string CsvSink::sanitize_filename(std::string const& val) {
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

std::string CsvSink::escape_csv(std::string const& val) {
   bool needs_quotes = false;
   for (char c : val) {
      if (c == ',' || c == '"' || c == '\n' || c == '\r') {
         needs_quotes = true;
         break;
      }
   }
   if (!needs_quotes) {
      return val;
   }
   std::string out = "\"";
   for (char c : val) {
      if (c == '"') {
         out += "\"\"";
      } else {
         out.push_back(c);
      }
   }
   out.push_back('"');
   return out;
}

std::ofstream& CsvSink::get_or_open_stream(std::string const& dut_name) {
   auto it = m_streams.find(dut_name);
   if (it != m_streams.end() && it->second.is_open()) {
      return it->second;
   }
   std::filesystem::path file_path =
       std::filesystem::path(m_cfg.directory) / (sanitize_filename(dut_name) + ".csv");
   bool write_header =
       !std::filesystem::exists(file_path) || std::filesystem::file_size(file_path) == 0;

   std::ofstream ofs(file_path, std::ios::out | std::ios::app);
   if (!ofs) {
      throw SinkError("Failed to open CSV sink file: " + file_path.string());
   }
   if (write_header) {
      ofs << "timestamp_ns,dut_name,dut_ip,metric_name,oid,oid_index,snmp_type,type_tag,value,raw_"
             "value,status\n";
   }
   auto [inserted_it, _] = m_streams.emplace(dut_name, std::move(ofs));
   return inserted_it->second;
}

void CsvSink::write_batch(Batch const& batch) {
   if (!m_cfg.enabled) {
      return;
   }
   std::lock_guard<std::mutex> lock(m_mutex);
   std::ofstream& ofs = get_or_open_stream(batch.dut_name);
   for (auto const& s : batch.samples) {
      std::string typed_val;
      if (s.type_tag == TypeTag::Int64) {
         typed_val = std::to_string(s.i64);
      } else if (s.type_tag == TypeTag::Float64) {
         typed_val = std::to_string(s.f64);
      } else if (s.type_tag == TypeTag::Str) {
         typed_val = s.str_val;
      }

      ofs << batch.timestamp_ns << "," << escape_csv(batch.dut_name) << ","
          << escape_csv(batch.dut_ip) << "," << escape_csv(s.metric_name) << ","
          << escape_csv(s.oid) << "," << escape_csv(s.oid_index) << "," << escape_csv(s.snmp_type)
          << "," << static_cast<int>(s.type_tag) << "," << escape_csv(typed_val) << ","
          << escape_csv(s.raw_value) << "," << static_cast<int>(s.status) << "\n";
   }
   ++m_batches_since_flush;
   if (m_cfg.flush_every_n_batches <= 1 || m_batches_since_flush >= m_cfg.flush_every_n_batches) {
      ofs.flush();
      m_batches_since_flush = 0;
   }
}

void CsvSink::flush() {
   std::lock_guard<std::mutex> lock(m_mutex);
   for (auto& kv : m_streams) {
      if (kv.second.is_open()) {
         kv.second.flush();
      }
   }
   m_batches_since_flush = 0;
}

} // namespace purpleair_data_logger
