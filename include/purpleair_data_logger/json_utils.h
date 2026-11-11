#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace purpleair_data_logger {
namespace json {

enum class Type { Null, Bool, Number, String, Array, Object };

class Value {
  public:
   using Array = std::vector<Value>;
   using Object = std::vector<std::pair<std::string, Value>>;

   Value() : m_type(Type::Null) {}
   explicit Value(bool b) : m_type(Type::Bool), m_bool(b) {}
   explicit Value(int v)
       : m_type(Type::Number), m_num(static_cast<double>(v)), m_int(v), m_is_int(true) {}
   explicit Value(int64_t v)
       : m_type(Type::Number), m_num(static_cast<double>(v)), m_int(v), m_is_int(true) {}
   explicit Value(double v) : m_type(Type::Number), m_num(v), m_int(static_cast<int64_t>(v)) {}
   explicit Value(std::string s) : m_type(Type::String), m_str(std::move(s)) {}
   explicit Value(char const* s) : m_type(Type::String), m_str(s ? s : "") {}
   explicit Value(Array a) : m_type(Type::Array), m_arr(std::move(a)) {}
   explicit Value(Object o) : m_type(Type::Object), m_obj(std::move(o)) {}

   static Value make_object() { return Value(Object{}); }
   static Value make_array() { return Value(Array{}); }

   Type type() const { return m_type; }
   bool is_null() const { return m_type == Type::Null; }
   bool is_bool() const { return m_type == Type::Bool; }
   bool is_number() const { return m_type == Type::Number; }
   bool is_int() const { return m_type == Type::Number && m_is_int; }
   bool is_string() const { return m_type == Type::String; }
   bool is_array() const { return m_type == Type::Array; }
   bool is_object() const { return m_type == Type::Object; }

   bool as_bool(bool default_val = false) const;
   int64_t as_int64(int64_t default_val = 0) const;
   int as_int(int default_val = 0) const;
   double as_double(double default_val = 0.0) const;
   std::string as_string(std::string const& default_val = "") const;

   Array const& as_array() const { return m_arr; }
   Array& as_array() { return m_arr; }
   Object const& as_object() const { return m_obj; }
   Object& as_object() { return m_obj; }

   bool contains(std::string const& key) const;
   Value const& get(std::string const& key) const;
   Value& operator[](std::string const& key);
   void set(std::string const& key, Value val);
   void push_back(Value val);

   std::string dump(int indent = -1) const;
   static Value parse(std::string const& text);

  private:
   void dump_impl(std::string& out, int indent, int depth) const;

   Type m_type = Type::Null;
   bool m_bool = false;
   double m_num = 0.0;
   int64_t m_int = 0;
   bool m_is_int = false;
   std::string m_str;
   Array m_arr;
   Object m_obj;
};

std::string escape_string(std::string const& s);

} // namespace json
} // namespace purpleair_data_logger
