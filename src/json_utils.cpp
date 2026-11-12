#include "purpleair_data_logger/json_utils.h"

#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <sstream>

#include "purpleair_data_logger/exceptions.h"

namespace purpleair_data_logger {
namespace json {

namespace {
Value const kNullValue;

class Parser {
  public:
   explicit Parser(std::string const& src) : m_src(src) {}

   Value parse_root() {
      skip_ws();
      if (m_pos >= m_src.size()) {
         throw ConfigError("JSON parse error: empty input");
      }
      Value v = parse_value();
      skip_ws();
      if (m_pos != m_src.size()) {
         throw error("unexpected trailing characters");
      }
      return v;
   }

  private:
   void skip_ws() {
      while (m_pos < m_src.size()) {
         char c = m_src[m_pos];
         if (c == ' ' || c == '\t' || c == '\r') {
            ++m_pos;
            ++m_col;
         } else if (c == '\n') {
            ++m_pos;
            ++m_line;
            m_col = 1;
         } else {
            break;
         }
      }
   }

   char peek() const { return m_pos < m_src.size() ? m_src[m_pos] : '\0'; }

   char get() {
      if (m_pos >= m_src.size()) {
         throw error("unexpected end of input");
      }
      char c = m_src[m_pos++];
      if (c == '\n') {
         ++m_line;
         m_col = 1;
      } else {
         ++m_col;
      }
      return c;
   }

   ConfigError error(std::string const& msg) const {
      std::ostringstream oss;
      oss << "JSON parse error at line " << m_line << ", column " << m_col << ": " << msg;
      return ConfigError(oss.str());
   }

   Value parse_value() {
      skip_ws();
      char c = peek();
      if (c == '{') {
         return parse_object();
      }
      if (c == '[') {
         return parse_array();
      }
      if (c == '"') {
         return Value(parse_string());
      }
      if (c == 't' || c == 'f') {
         return parse_bool();
      }
      if (c == 'n') {
         return parse_null();
      }
      if (c == '-' || std::isdigit(static_cast<unsigned char>(c))) {
         return parse_number();
      }
      throw error(std::string("unexpected character '") + c + "'");
   }

   Value parse_object() {
      get();
      skip_ws();
      Value::Object obj;
      if (peek() == '}') {
         get();
         return Value(std::move(obj));
      }
      while (true) {
         skip_ws();
         if (peek() != '"') {
            throw error("expected string key in object");
         }
         std::string key = parse_string();
         skip_ws();
         if (get() != ':') {
            throw error("expected ':' after object key");
         }
         Value val = parse_value();
         bool replaced = false;
         for (auto& kv : obj) {
            if (kv.first == key) {
               kv.second = std::move(val);
               replaced = true;
               break;
            }
         }
         if (!replaced) {
            obj.emplace_back(std::move(key), std::move(val));
         }
         skip_ws();
         char sep = get();
         if (sep == '}') {
            break;
         }
         if (sep != ',') {
            throw error("expected ',' or '}' in object");
         }
      }
      return Value(std::move(obj));
   }

   Value parse_array() {
      get();
      skip_ws();
      Value::Array arr;
      if (peek() == ']') {
         get();
         return Value(std::move(arr));
      }
      while (true) {
         arr.push_back(parse_value());
         skip_ws();
         char sep = get();
         if (sep == ']') {
            break;
         }
         if (sep != ',') {
            throw error("expected ',' or ']' in array");
         }
      }
      return Value(std::move(arr));
   }

   static void append_utf8(std::string& out, uint32_t cp) {
      if (cp <= 0x7F) {
         out.push_back(static_cast<char>(cp));
      } else if (cp <= 0x7FF) {
         out.push_back(static_cast<char>(0xC0 | ((cp >> 6) & 0x1F)));
         out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
      } else if (cp <= 0xFFFF) {
         out.push_back(static_cast<char>(0xE0 | ((cp >> 12) & 0x0F)));
         out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
         out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
      } else {
         out.push_back(static_cast<char>(0xF0 | ((cp >> 18) & 0x07)));
         out.push_back(static_cast<char>(0x80 | ((cp >> 12) & 0x3F)));
         out.push_back(static_cast<char>(0x80 | ((cp >> 6) & 0x3F)));
         out.push_back(static_cast<char>(0x80 | (cp & 0x3F)));
      }
   }

   uint32_t parse_hex4() {
      uint32_t val = 0;
      for (int i = 0; i < 4; ++i) {
         char c = get();
         val <<= 4;
         if (c >= '0' && c <= '9') {
            val |= static_cast<uint32_t>(c - '0');
         } else if (c >= 'a' && c <= 'f') {
            val |= static_cast<uint32_t>(c - 'a' + 10);
         } else if (c >= 'A' && c <= 'F') {
            val |= static_cast<uint32_t>(c - 'A' + 10);
         } else {
            throw error("invalid hex digit in \\u escape");
         }
      }
      return val;
   }

   std::string parse_string() {
      if (get() != '"') {
         throw error("expected '\"'");
      }
      std::string out;
      while (true) {
         char c = get();
         if (c == '"') {
            break;
         }
         if (static_cast<unsigned char>(c) < 0x20) {
            throw error("unescaped control character in string");
         }
         if (c == '\\') {
            char esc = get();
            switch (esc) {
               case '"':
                  out.push_back('"');
                  break;
               case '\\':
                  out.push_back('\\');
                  break;
               case '/':
                  out.push_back('/');
                  break;
               case 'b':
                  out.push_back('\b');
                  break;
               case 'f':
                  out.push_back('\f');
                  break;
               case 'n':
                  out.push_back('\n');
                  break;
               case 'r':
                  out.push_back('\r');
                  break;
               case 't':
                  out.push_back('\t');
                  break;
               case 'u': {
                  uint32_t cp = parse_hex4();
                  if (cp >= 0xD800 && cp <= 0xDBFF && peek() == '\\') {
                     size_t saved = m_pos;
                     get();
                     if (peek() == 'u') {
                        get();
                        uint32_t low = parse_hex4();
                        if (low >= 0xDC00 && low <= 0xDFFF) {
                           cp = 0x10000 + (((cp - 0xD800) << 10) | (low - 0xDC00));
                        }
                     } else {
                        m_pos = saved;
                     }
                  }
                  append_utf8(out, cp);
                  break;
               }
               default:
                  throw error(std::string("invalid escape sequence \\") + esc);
            }
         } else {
            out.push_back(c);
         }
      }
      return out;
   }

   Value parse_bool() {
      if (m_src.compare(m_pos, 4, "true") == 0) {
         m_pos += 4;
         m_col += 4;
         return Value(true);
      }
      if (m_src.compare(m_pos, 5, "false") == 0) {
         m_pos += 5;
         m_col += 5;
         return Value(false);
      }
      throw error("invalid boolean literal");
   }

   Value parse_null() {
      if (m_src.compare(m_pos, 4, "null") == 0) {
         m_pos += 4;
         m_col += 4;
         return Value();
      }
      throw error("invalid null literal");
   }

   Value parse_number() {
      size_t start = m_pos;
      bool is_float = false;
      if (peek() == '-') {
         get();
      }
      if (!std::isdigit(static_cast<unsigned char>(peek()))) {
         throw error("invalid number");
      }
      if (peek() == '0') {
         get();
      } else {
         while (std::isdigit(static_cast<unsigned char>(peek()))) {
            get();
         }
      }
      if (peek() == '.') {
         is_float = true;
         get();
         if (!std::isdigit(static_cast<unsigned char>(peek()))) {
            throw error("expected digit after decimal point");
         }
         while (std::isdigit(static_cast<unsigned char>(peek()))) {
            get();
         }
      }
      if (peek() == 'e' || peek() == 'E') {
         is_float = true;
         get();
         if (peek() == '+' || peek() == '-') {
            get();
         }
         if (!std::isdigit(static_cast<unsigned char>(peek()))) {
            throw error("expected digit in exponent");
         }
         while (std::isdigit(static_cast<unsigned char>(peek()))) {
            get();
         }
      }
      std::string token = m_src.substr(start, m_pos - start);
      if (!is_float) {
         char* endptr = nullptr;
         long long iv = std::strtoll(token.c_str(), &endptr, 10);
         if (endptr && *endptr == '\0') {
            return Value(static_cast<int64_t>(iv));
         }
      }
      char* endptr = nullptr;
      double dv = std::strtod(token.c_str(), &endptr);
      return Value(dv);
   }

   std::string const& m_src;
   size_t m_pos = 0;
   size_t m_line = 1;
   size_t m_col = 1;
};

} // namespace

std::string escape_string(std::string const& s) {
   std::string out;
   out.reserve(s.size() + 2);
   for (unsigned char c : s) {
      switch (c) {
         case '"':
            out += "\\\"";
            break;
         case '\\':
            out += "\\\\";
            break;
         case '\b':
            out += "\\b";
            break;
         case '\f':
            out += "\\f";
            break;
         case '\n':
            out += "\\n";
            break;
         case '\r':
            out += "\\r";
            break;
         case '\t':
            out += "\\t";
            break;
         default:
            if (c < 0x20) {
               char buf[8];
               std::snprintf(buf, sizeof(buf), "\\u%04x", static_cast<unsigned int>(c));
               out += buf;
            } else {
               out.push_back(static_cast<char>(c));
            }
            break;
      }
   }
   return out;
}

bool Value::as_bool(bool default_val) const {
   if (m_type == Type::Bool) {
      return m_bool;
   }
   return default_val;
}

int64_t Value::as_int64(int64_t default_val) const {
   if (m_type == Type::Number) {
      return m_is_int ? m_int : static_cast<int64_t>(m_num);
   }
   return default_val;
}

int Value::as_int(int default_val) const { return static_cast<int>(as_int64(default_val)); }

double Value::as_double(double default_val) const {
   if (m_type == Type::Number) {
      return m_is_int ? static_cast<double>(m_int) : m_num;
   }
   return default_val;
}

std::string Value::as_string(std::string const& default_val) const {
   if (m_type == Type::String) {
      return m_str;
   }
   return default_val;
}

bool Value::contains(std::string const& key) const {
   if (m_type != Type::Object) {
      return false;
   }
   for (auto const& kv : m_obj) {
      if (kv.first == key) {
         return true;
      }
   }
   return false;
}

Value const& Value::get(std::string const& key) const {
   if (m_type == Type::Object) {
      for (auto const& kv : m_obj) {
         if (kv.first == key) {
            return kv.second;
         }
      }
   }
   return kNullValue;
}

Value& Value::operator[](std::string const& key) {
   if (m_type != Type::Object) {
      m_type = Type::Object;
      m_obj.clear();
   }
   for (auto& kv : m_obj) {
      if (kv.first == key) {
         return kv.second;
      }
   }
   m_obj.emplace_back(key, Value());
   return m_obj.back().second;
}

void Value::set(std::string const& key, Value val) { (*this)[key] = std::move(val); }

void Value::push_back(Value val) {
   if (m_type != Type::Array) {
      m_type = Type::Array;
      m_arr.clear();
   }
   m_arr.push_back(std::move(val));
}

void Value::dump_impl(std::string& out, int indent, int depth) const {
   switch (m_type) {
      case Type::Null:
         out += "null";
         break;
      case Type::Bool:
         out += (m_bool ? "true" : "false");
         break;
      case Type::Number:
         if (m_is_int) {
            out += std::to_string(m_int);
         } else if (std::isnan(m_num) || std::isinf(m_num)) {
            out += "null";
         } else {
            std::ostringstream oss;
            oss.precision(12);
            oss << m_num;
            out += oss.str();
         }
         break;
      case Type::String:
         out.push_back('"');
         out += escape_string(m_str);
         out.push_back('"');
         break;
      case Type::Array: {
         if (m_arr.empty()) {
            out += "[]";
            break;
         }
         out.push_back('[');
         for (size_t i = 0; i < m_arr.size(); ++i) {
            if (i > 0) {
               out.push_back(',');
            }
            if (indent >= 0) {
               out.push_back('\n');
               out.append(static_cast<size_t>((depth + 1) * indent), ' ');
            }
            m_arr[i].dump_impl(out, indent, depth + 1);
         }
         if (indent >= 0) {
            out.push_back('\n');
            out.append(static_cast<size_t>(depth * indent), ' ');
         }
         out.push_back(']');
         break;
      }
      case Type::Object: {
         if (m_obj.empty()) {
            out += "{}";
            break;
         }
         out.push_back('{');
         for (size_t i = 0; i < m_obj.size(); ++i) {
            if (i > 0) {
               out.push_back(',');
            }
            if (indent >= 0) {
               out.push_back('\n');
               out.append(static_cast<size_t>((depth + 1) * indent), ' ');
            }
            out.push_back('"');
            out += escape_string(m_obj[i].first);
            out += (indent >= 0) ? "\": " : "\":";
            m_obj[i].second.dump_impl(out, indent, depth + 1);
         }
         if (indent >= 0) {
            out.push_back('\n');
            out.append(static_cast<size_t>(depth * indent), ' ');
         }
         out.push_back('}');
         break;
      }
   }
}

std::string Value::dump(int indent) const {
   std::string out;
   dump_impl(out, indent, 0);
   return out;
}

Value Value::parse(std::string const& text) {
   Parser p(text);
   return p.parse_root();
}

} // namespace json
} // namespace purpleair_data_logger
