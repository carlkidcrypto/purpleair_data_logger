#pragma once

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <thread>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace purpleair_dl_test {

class TempDir {
  public:
   explicit TempDir(std::string const& prefix) {
      static std::atomic<uint64_t> counter{0};
      auto base = std::filesystem::temp_directory_path();
      auto ts = std::chrono::steady_clock::now().time_since_epoch().count();
      auto seq = ++counter;
      m_path = base / (prefix + "_" + std::to_string(ts) + "_" + std::to_string(seq));
      std::filesystem::create_directories(m_path);
   }
   ~TempDir() {
      std::error_code ec;
      std::filesystem::remove_all(m_path, ec);
   }
   std::filesystem::path const& path() const { return m_path; }
   std::string str() const { return m_path.string(); }

  private:
   std::filesystem::path m_path;
};

inline std::string read_file_contents(std::filesystem::path const& p) {
   std::ifstream ifs(p, std::ios::in | std::ios::binary);
   std::ostringstream oss;
   oss << ifs.rdbuf();
   return oss.str();
}

// Lightweight loopback HTTP server serving a mock PurpleAir local sensor /json payload
class LoopbackHttpJsonServer {
  public:
   explicit LoopbackHttpJsonServer(std::string json_body) : m_body(std::move(json_body)) {
#ifdef _WIN32
      WSADATA wsa;
      WSAStartup(MAKEWORD(2, 2), &wsa);
#endif
      m_listen_fd = ::socket(AF_INET, SOCK_STREAM, 0);
      int opt = 1;
#ifdef _WIN32
      setsockopt(m_listen_fd, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<char const*>(&opt),
                 sizeof(opt));
#else
      setsockopt(m_listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
      sockaddr_in addr{};
      addr.sin_family = AF_INET;
      addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
      addr.sin_port = htons(0);
      ::bind(m_listen_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
      ::listen(m_listen_fd, 16);

      sockaddr_in bound{};
#ifdef _WIN32
      int len = sizeof(bound);
#else
      socklen_t len = sizeof(bound);
#endif
      ::getsockname(m_listen_fd, reinterpret_cast<sockaddr*>(&bound), &len);
      m_port = ntohs(bound.sin_port);

      m_running.store(true);
      m_thread = std::thread([this]() { serve_loop(); });
   }

   ~LoopbackHttpJsonServer() { stop(); }

   int port() const { return m_port; }

   void stop() {
      if (!m_running.exchange(false)) {
         return;
      }
      if (m_listen_fd >= 0) {
#ifdef _WIN32
         closesocket(m_listen_fd);
#else
         ::shutdown(m_listen_fd, SHUT_RDWR);
         ::close(m_listen_fd);
#endif
         m_listen_fd = -1;
      }
      if (m_thread.joinable()) {
         m_thread.join();
      }
   }

  private:
   void serve_loop() {
      while (m_running.load()) {
         sockaddr_in caddr{};
#ifdef _WIN32
         int clen = sizeof(caddr);
         int cfd =
             static_cast<int>(::accept(m_listen_fd, reinterpret_cast<sockaddr*>(&caddr), &clen));
#else
         socklen_t clen = sizeof(caddr);
         int cfd = ::accept(m_listen_fd, reinterpret_cast<sockaddr*>(&caddr), &clen);
#endif
         if (cfd < 0) {
            break;
         }
         char buf[1024];
#ifdef _WIN32
         ::recv(cfd, buf, sizeof(buf), 0);
#else
         (void)::read(cfd, buf, sizeof(buf));
#endif
         std::string resp =
             "HTTP/1.1 200 OK\r\n"
             "Content-Type: application/json\r\n"
             "Content-Length: " +
             std::to_string(m_body.size()) +
             "\r\n"
             "Connection: close\r\n\r\n" +
             m_body;
#ifdef _WIN32
         ::send(cfd, resp.data(), static_cast<int>(resp.size()), 0);
         closesocket(cfd);
#else
         (void)::write(cfd, resp.data(), resp.size());
         ::close(cfd);
#endif
      }
   }

   std::string m_body;
   int m_listen_fd = -1;
   int m_port = 0;
   std::atomic<bool> m_running{false};
   std::thread m_thread;
};

} // namespace purpleair_dl_test
