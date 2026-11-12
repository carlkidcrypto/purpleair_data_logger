#pragma once

#include <chrono>
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>

namespace purpleair_data_logger {

template <typename T>
class BoundedQueue {
  public:
   explicit BoundedQueue(size_t capacity = 4096) : m_capacity(capacity == 0 ? 1 : capacity) {}

   bool try_push(T item) {
      std::unique_lock<std::mutex> lock(m_mutex);
      if (m_closed || m_queue.size() >= m_capacity) {
         return false;
      }
      m_queue.push_back(std::move(item));
      lock.unlock();
      m_not_empty.notify_one();
      return true;
   }

   bool push_wait(T item, std::chrono::milliseconds timeout) {
      std::unique_lock<std::mutex> lock(m_mutex);
      if (!m_not_full.wait_for(lock, timeout,
                               [this]() { return m_closed || m_queue.size() < m_capacity; })) {
         return false;
      }
      if (m_closed) {
         return false;
      }
      m_queue.push_back(std::move(item));
      lock.unlock();
      m_not_empty.notify_one();
      return true;
   }

   std::optional<T> pop_wait(std::chrono::milliseconds timeout) {
      std::unique_lock<std::mutex> lock(m_mutex);
      if (!m_not_empty.wait_for(lock, timeout, [this]() { return m_closed || !m_queue.empty(); })) {
         return std::nullopt;
      }
      if (m_queue.empty()) {
         return std::nullopt;
      }
      T item = std::move(m_queue.front());
      m_queue.pop_front();
      lock.unlock();
      m_not_full.notify_one();
      return item;
   }

   void close() {
      std::lock_guard<std::mutex> lock(m_mutex);
      m_closed = true;
      m_not_empty.notify_all();
      m_not_full.notify_all();
   }

   void reopen() {
      std::lock_guard<std::mutex> lock(m_mutex);
      m_closed = false;
   }

   size_t size() const {
      std::lock_guard<std::mutex> lock(m_mutex);
      return m_queue.size();
   }

   size_t capacity() const { return m_capacity; }

   bool is_closed() const {
      std::lock_guard<std::mutex> lock(m_mutex);
      return m_closed;
   }

  private:
   size_t m_capacity;
   mutable std::mutex m_mutex;
   std::condition_variable m_not_empty;
   std::condition_variable m_not_full;
   std::deque<T> m_queue;
   bool m_closed = false;
};

} // namespace purpleair_data_logger
