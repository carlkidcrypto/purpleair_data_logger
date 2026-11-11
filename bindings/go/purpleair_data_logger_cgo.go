package purpleair_data_logger

// #cgo CXXFLAGS: -std=c++17 -I${SRCDIR}/../../include
// #cgo darwin LDFLAGS: -L${SRCDIR}/lib -lpurpleair_data_logger -Wl,-rpath,${SRCDIR}/lib
// #cgo linux LDFLAGS: -L${SRCDIR}/lib -lpurpleair_data_logger -Wl,-rpath,${SRCDIR}/lib -pthread
// #cgo windows LDFLAGS: -L${SRCDIR}/lib -lpurpleair_data_logger -lws2_32
import "C"
