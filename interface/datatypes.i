%include "purpleair_data_logger/version.h"
%include "purpleair_data_logger/datatypes.h"

namespace std {
   %template(StringVector) vector<std::string>;
   %template(SampleVector) vector<purpleair_data_logger::Sample>;
   %template(BatchVector) vector<purpleair_data_logger::Batch>;
   %template(SinkRowVector) vector<purpleair_data_logger::SinkRow>;
}
