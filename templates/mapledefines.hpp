#ifndef MAPLE_DEFINES_HPP__
#define MAPLE_DEFINES_HPP__

#include <Eigen/Core>
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

namespace py = pybind11;

namespace maple {

    typedef float float_t;
    typedef Eigen::MatrixXd Matrix;
    typedef Eigen::VectorXd Vector;
    typedef py::EigenDRef<Matrix> MatrixRef;
    typedef py::EigenDRef<Vector> VectorRef;


} // namespace maple

#endif // MAPLE_DEFINES_HPP__
