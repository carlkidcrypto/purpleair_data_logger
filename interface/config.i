%include "purpleair_data_logger/config.h"

namespace std {
   %template(MetricConfigVector) vector<purpleair_data_logger::MetricConfig>;
   %template(DutConfigVector) vector<purpleair_data_logger::DutConfig>;
}
