%exception {
   try {
      $action
   } catch (const purpleair_data_logger::ConfigError& e) {
      SWIG_exception(SWIG_ValueError, e.what());
   } catch (const purpleair_data_logger::SinkError& e) {
      SWIG_exception(SWIG_RuntimeError, e.what());
   } catch (const purpleair_data_logger::PollerError& e) {
      SWIG_exception(SWIG_RuntimeError, e.what());
   } catch (const purpleair_data_logger::DataLoggerError& e) {
      SWIG_exception(SWIG_RuntimeError, e.what());
   } catch (const std::invalid_argument& e) {
      SWIG_exception(SWIG_ValueError, e.what());
   } catch (const std::exception& e) {
      SWIG_exception(SWIG_RuntimeError, e.what());
   } catch (...) {
      SWIG_exception(SWIG_RuntimeError, "Unknown C++ exception in purpleair_data_logger");
   }
}
