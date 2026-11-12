%module(threads="1") purpleair_data_logger

%{
#include "purpleair_data_logger/version.h"
#include "purpleair_data_logger/exceptions.h"
#include "purpleair_data_logger/datatypes.h"
#include "purpleair_data_logger/config.h"
#include "purpleair_data_logger/sink.h"
#include "purpleair_data_logger/data_logger.h"
#include "purpleair_data_logger/cli_runner.h"
%}

%include <std_string.i>
%include <std_vector.i>
%include <stdint.i>
%include <exception.i>

%include "exceptions.i"
%include "datatypes.i"
%include "config.i"
%include "data_logger.i"
