#if defined(SWIGPYTHON)
%thread purpleair_data_logger::DataLogger::run;
%thread purpleair_data_logger::DataLogger::run_once;
%thread purpleair_data_logger::DataLogger::stop;
%thread purpleair_data_logger::DataLogger::probe_dut;
%thread purpleair_data_logger::DataLogger::probe_dut_json;
%thread purpleair_data_logger::DataLogger::request_json;
%thread purpleair_data_logger::DataLogger::set_json;
%thread purpleair_data_logger::CliRunner::run;
%thread purpleair_data_logger::CliRunner::execute;
#endif

%ignore purpleair_data_logger::ISink;
%ignore purpleair_data_logger::create_sinks;
%ignore purpleair_data_logger::CliRunner::run_streams;
%ignore purpleair_data_logger::DataLogger::operator=;
%ignore purpleair_data_logger::DataLogger::DataLogger(DataLogger&&);

%include "purpleair_data_logger/sink.h"
%include "purpleair_data_logger/data_logger.h"
%include "purpleair_data_logger/cli_runner.h"
