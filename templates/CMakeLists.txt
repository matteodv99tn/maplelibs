cmake_minimum_required(VERSION 3.4)
project(pymodule_example)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DNDEBUG -O3")

find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories("/usr/include/eigen3")

set(SOURCE_FILE_DIR ${CMAKE_CURRENT_LIST_DIR}/src)
set(WRAPPER_FILE_DIR ${CMAKE_CURRENT_LIST_DIR}/pythonwraps)
set(MODULE_INSTALL_DIR ${CMAKE_CURRENT_LIST_DIR}/lib)

add_subdirectory("pythonwraps")
