#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <maple_codegen/$headername.hpp>

namespace py = pybind11;


PYBIND11_MODULE($modulename, m) {
    m.doc() = "Maple generated code for the function $modulename";
    $wrap_defs
}


