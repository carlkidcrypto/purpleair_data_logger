#include "purpleair_data_logger/prometheus_sink.h"

#include <atomic>
#include <cctype>
#include <cstring>
#include <map>
#include <mutex>
#include <sstream>
#include <thread>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

#include "purpleair_data_logger/exceptions.h"

namespace purpleair_data_logger {

namespace {
std::string sanitize_prom_name(std::string const& s) {
   std::string out;
   out.reserve(s.size());
   for (size_t i = 0; i < s.size(); ++i) {
      unsigned char c = static_cast<unsigned char>(s[i]);
      if (std::isalnum(c) || c == '_') {
         out.push_back(static_cast<char>(c));
      } else {
         out.push_back('_');
      }
   }
   if (!out.empty() && std::isdigit(static_cast<unsigned char>(out[0]))) {
      out.insert(out.begin(), '_');
   }
   return out.empty() ? "metric" : out;
}

std::string escape_prom_label(std::string const& s) {
   std::string out;
   for (char c : s) {
      if (c == '\\') {
         out += "\\\\";
      } else if (c == '"') {
         out += "\\\"";
      } else if (c == '\n') {
         out += "\\n";
      } else {
         out.push_back(c);
      }
   }
   return out;
}

void close_socket_fd(int fd) {
#ifdef _WIN32
   closesocket(fd);
#else
   close(fd);
#endif
}
} // namespace

struct PrometheusSink::Impl {
   PrometheusSinkConfig cfg;
   mutable std::mutex mutex;
   std::map<std::string, double> gauges;
   uint64_t batches_total = 0;
   uint64_t samples_total = 0;

   std::atomic<bool> stop_flag{false};
   int listen_fd = -1;
   int actual_port = 0;
   std::thread server_thread;

   void start_server() {
#ifdef _WIN32
      WSADATA wsaData;
      WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
      listen_fd = static_cast<int>(socket(AF_INET, SOCK_STREAM, 0));
      if (listen_fd < 0) {
         return;
      }
      int opt = 1;
#ifdef _WIN32
      setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<char const*>(&opt),
                 sizeof(opt));
#else
      setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
      sockaddr_in addr{};
      addr.sin_family = AF_INET;
      addr.sin_port = htons(static_cast<uint16_t>(cfg.port));
      if (inet_pton(AF_INET, cfg.bind_host.c_str(), &addr.sin_addr) <= 0) {
         addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
      }
      if (bind(listen_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
         close_socket_fd(listen_fd);
         listen_fd = -1;
         return;
      }
      sockaddr_in bound{};
#ifdef _WIN32
      int len = sizeof(bound);
#else
      socklen_t len = sizeof(bound);
#endif
      if (getsockname(listen_fd, reinterpret_cast<sockaddr*>(&bound), &len) == 0) {
         actual_port = ntohs(bound.sin_port);
      }
      if (listen(listen_fd, 8) < 0) {
         close_socket_fd(listen_fd);
         listen_fd = -1;
         return;
      }

      server_thread = std::thread([this]() {
         while (!stop_flag.load()) {
            fd_set readfds;
            FD_ZERO(&readfds);
            FD_SET(listen_fd, &readfds);
            timeval tv{};
            tv.tv_sec = 0;
            tv.tv_usec = 100000;
            int sel = select(listen_fd + 1, &readfds, nullptr, nullptr, &tv);
            if (sel <= 0 || stop_flag.load()) {
               continue;
            }
            sockaddr_in cli{};
#ifdef _WIN32
            int clilen = sizeof(cli);
#else
            socklen_t clilen = sizeof(cli);
#endif
            int cfd =
                static_cast<int>(accept(listen_fd, reinterpret_cast<sockaddr*>(&cli), &clilen));
            if (cfd < 0) {
               continue;
            }
            char buf[1024];
#ifdef _WIN32
            recv(cfd, buf, sizeof(buf), 0);
#else
            (void)read(cfd, buf, sizeof(buf));
#endif
            std::string body = render();
            std::ostringstream resp;
            resp << "HTTP/1.1 200 OK\r\n"
                 << "Content-Type: text/plain; version=0.0.4; charset=utf-8\r\n"
                 << "Content-Length: " << body.size() << "\r\n"
                 << "Connection: close\r\n\r\n"
                 << body;
            std::string wire = resp.str();
#ifdef _WIN32
            send(cfd, wire.data(), static_cast<int>(wire.size()), 0);
#else
            (void)write(cfd, wire.data(), wire.size());
#endif
            close_socket_fd(cfd);
         }
      });
   }

   void stop_server() {
      stop_flag.store(true);
      if (listen_fd >= 0) {
         close_socket_fd(listen_fd);
         listen_fd = -1;
      }
      if (server_thread.joinable()) {
         server_thread.join();
      }
   }

   std::string render() const {
      std::lock_guard<std::mutex> lock(mutex);
      std::string prefix = sanitize_prom_name(cfg.metric_prefix);
      std::ostringstream oss;
      oss << "# HELP " << prefix << "_batches_total Total batches written to Prometheus sink\n"
          << "# TYPE " << prefix << "_batches_total counter\n"
          << prefix << "_batches_total " << batches_total << "\n"
          << "# HELP " << prefix << "_samples_total Total samples processed by Prometheus sink\n"
          << "# TYPE " << prefix << "_samples_total counter\n"
          << prefix << "_samples_total " << samples_total << "\n";
      for (auto const& kv : gauges) {
         oss << kv.first << " " << kv.second << "\n";
      }
      return oss.str();
   }
};

PrometheusSink::PrometheusSink(PrometheusSinkConfig config) : m_impl(std::make_unique<Impl>()) {
   m_impl->cfg = std::move(config);
   if (m_impl->cfg.enabled) {
      m_impl->start_server();
   }
}

PrometheusSink::~PrometheusSink() {
   if (m_impl) {
      m_impl->stop_server();
   }
}

void PrometheusSink::write_batch(Batch const& batch) {
   if (!m_impl->cfg.enabled) {
      return;
   }
   std::lock_guard<std::mutex> lock(m_impl->mutex);
   std::string prefix = sanitize_prom_name(m_impl->cfg.metric_prefix);
   ++m_impl->batches_total;
   m_impl->samples_total += batch.samples.size();
   for (auto const& s : batch.samples) {
      if (s.type_tag != TypeTag::Int64 && s.type_tag != TypeTag::Float64) {
         continue;
      }
      double val = (s.type_tag == TypeTag::Int64) ? static_cast<double>(s.i64) : s.f64;
      std::string mname = prefix + "_" + sanitize_prom_name(s.metric_name);
      std::string line = mname + "{dut=\"" + escape_prom_label(batch.dut_name) + "\",dut_ip=\"" +
                         escape_prom_label(batch.dut_ip) + "\",oid=\"" + escape_prom_label(s.oid) +
                         "\",oid_index=\"" + escape_prom_label(s.oid_index) + "\"}";
      m_impl->gauges[line] = val;
   }
}

void PrometheusSink::flush() {}

std::string PrometheusSink::render_metrics() const { return m_impl->render(); }

int PrometheusSink::bound_port() const { return m_impl->actual_port; }

} // namespace purpleair_data_logger
