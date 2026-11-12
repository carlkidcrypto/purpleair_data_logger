#include <gtest/gtest.h>

#include <cmath>
#include <limits>
#include <string>

#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/json_utils.h"

using namespace purpleair_data_logger;
using namespace purpleair_data_logger::json;

TEST(JsonUtilsTest, ParsePrimitivesObjectsAndArrays) {
   std::string src = R"({
      "null_val": null,
      "bool_t": true,
      "bool_f": false,
      "int_pos": 42,
      "int_neg": -100,
      "zero": 0,
      "float_val": 3.1415,
      "exp_pos": 1.5e+2,
      "exp_neg": 2.5E-2,
      "str_escapes": "quote:\" slash:\\ fwd:\/ bs:\b ff:\f nl:\n cr:\r tab:\t",
      "unicode_1b": "\u0041",
      "unicode_2b": "\u00DF",
      "unicode_3b": "\u20AC",
      "surrogate_pair": "\uD83D\uDE00",
      "surrogate_unpaired": "\uD800\n",
      "surrogate_non_low": "\uD800\u0041",
      "dup_key": "first",
      "dup_key": "second",
      "empty_obj": {},
      "empty_arr": [],
      "arr": [1, "two", false, null]
   })";

   Value root = Value::parse(src);
   ASSERT_TRUE(root.is_object());
   EXPECT_TRUE(root.get("null_val").is_null());
   EXPECT_TRUE(root.get("bool_t").is_bool());
   EXPECT_TRUE(root.get("bool_t").as_bool());
   EXPECT_FALSE(root.get("bool_f").as_bool(true));
   EXPECT_EQ(root.get("null_val").as_bool(true), true);

   EXPECT_TRUE(root.get("int_pos").is_int());
   EXPECT_EQ(root.get("int_pos").as_int(), 42);
   EXPECT_EQ(root.get("int_neg").as_int64(), -100);
   EXPECT_EQ(root.get("zero").as_int(), 0);
   EXPECT_NEAR(root.get("int_pos").as_double(), 42.0, 1e-9);
   EXPECT_EQ(root.get("null_val").as_int64(99), 99);

   EXPECT_TRUE(root.get("float_val").is_number());
   EXPECT_NEAR(root.get("float_val").as_double(), 3.1415, 1e-6);
   EXPECT_EQ(root.get("float_val").as_int64(), 3);
   EXPECT_NEAR(root.get("exp_pos").as_double(), 150.0, 1e-6);
   EXPECT_NEAR(root.get("exp_neg").as_double(), 0.025, 1e-6);
   EXPECT_NEAR(root.get("null_val").as_double(7.5), 7.5, 1e-6);

   EXPECT_TRUE(root.get("unicode_1b").is_string());
   EXPECT_EQ(root.get("unicode_1b").as_string(), "A");
   EXPECT_FALSE(root.get("unicode_2b").as_string().empty());
   EXPECT_FALSE(root.get("unicode_3b").as_string().empty());
   EXPECT_EQ(root.get("surrogate_pair").as_string().size(), 4u);
   EXPECT_EQ(root.get("dup_key").as_string(), "second");
   EXPECT_EQ(root.get("null_val").as_string("fallback"), "fallback");

   EXPECT_TRUE(root.contains("arr"));
   EXPECT_FALSE(root.contains("missing_key"));
   EXPECT_TRUE(root.get("missing_key").is_null());
   EXPECT_FALSE(root.get("arr").contains("nope"));
   EXPECT_TRUE(root.get("arr").get("nope").is_null());
}

TEST(JsonUtilsTest, MutatorsAndDumping) {
   Value v;
   v.push_back(Value(10));
   v.push_back(Value("text"));
   EXPECT_TRUE(v.is_array());
   EXPECT_EQ(v.as_array().size(), 2u);

   // Calling operator[] on an Array converts it to an Object
   v["alpha"] = Value(1);
   v["alpha"] = Value(2);
   v.set("beta", Value(std::numeric_limits<double>::quiet_NaN()));
   v.set("gamma", Value(std::numeric_limits<double>::infinity()));
   std::string ctrl_str(1, '\x05');
   ctrl_str += "\"\\\b\f\n\r\t";
   v.set("ctrl", Value(ctrl_str));
   v.set("arr", Value::make_array());
   v["arr"].push_back(Value(true));
   v["arr"].push_back(Value(false));
   v.set("empty_arr", Value::make_array());
   v.set("empty_obj", Value::make_object());

   std::string compact = v.dump(-1);
   std::string pretty = v.dump(2);
   EXPECT_NE(compact.find("\\u0005"), std::string::npos);
   EXPECT_NE(pretty.find("\"alpha\": 2"), std::string::npos);

   Value reparsed = Value::parse(pretty);
   EXPECT_EQ(reparsed.get("alpha").as_int(), 2);
   EXPECT_TRUE(reparsed.get("beta").is_null());
   EXPECT_TRUE(reparsed.get("gamma").is_null());
}

TEST(JsonUtilsTest, AllParserErrorBranches) {
   EXPECT_THROW(Value::parse(""), ConfigError);
   EXPECT_THROW(Value::parse("   \n\t  "), ConfigError);
   EXPECT_THROW(Value::parse("true false"), ConfigError);
   EXPECT_THROW(Value::parse("@"), ConfigError);
   EXPECT_THROW(Value::parse("{123: 1}"), ConfigError);
   EXPECT_THROW(Value::parse("{\"k\" 1}"), ConfigError);
   EXPECT_THROW(Value::parse("{\"k\": 1;}"), ConfigError);
   EXPECT_THROW(Value::parse("[1 2]"), ConfigError);
   EXPECT_THROW(Value::parse("\"unterminated"), ConfigError);
   EXPECT_THROW(Value::parse(std::string("\"\x01\"")), ConfigError);
   EXPECT_THROW(Value::parse("\"\\q\""), ConfigError);
   EXPECT_THROW(Value::parse("\"\\u12G4\""), ConfigError);
   EXPECT_THROW(Value::parse("tru"), ConfigError);
   EXPECT_THROW(Value::parse("fals"), ConfigError);
   EXPECT_THROW(Value::parse("nul"), ConfigError);
   EXPECT_THROW(Value::parse("-"), ConfigError);
   EXPECT_THROW(Value::parse("1."), ConfigError);
   EXPECT_THROW(Value::parse("1e"), ConfigError);
   EXPECT_THROW(Value::parse("1e+"), ConfigError);
}
