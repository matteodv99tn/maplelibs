cmake_minimum_required(VERSION 3.4)
project(pymodule_example)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 11)

find_package(pybind11 REQUIRED)
find_package(Eigen3 REQUIRED)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories("/usr/include/eigen3")

set(SOURCE_FILE_DIR ${CMAKE_CURRENT_LIST_DIR}/src)
set(WRAPPER_FILE_DIR ${CMAKE_CURRENT_LIST_DIR}/pythonwraps)
set(MODULE_INSTALL_DIR ${CMAKE_CURRENT_LIST_DIR}/lib)

add_subdirectory("pythonwraps")

