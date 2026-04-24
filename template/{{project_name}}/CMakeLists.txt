cmake_minimum_required(VERSION 3.16)

# Project name tracks the current directory, so the scaffold has no
# hardcoded identity anywhere. Sanitize to a C-identifier-safe form so
# folders with spaces, dots, or leading digits don't break project().
get_filename_component(_RAW_DIR_NAME "${CMAKE_SOURCE_DIR}" NAME)
string(REGEX REPLACE "[^A-Za-z0-9_]" "_" PROJECT_DIR_NAME "${_RAW_DIR_NAME}")
if(PROJECT_DIR_NAME MATCHES "^[0-9]")
    set(PROJECT_DIR_NAME "p_${PROJECT_DIR_NAME}")
endif()
if(NOT _RAW_DIR_NAME STREQUAL PROJECT_DIR_NAME)
    message(WARNING
        "Folder '${_RAW_DIR_NAME}' was sanitized to CMake project name "
        "'${PROJECT_DIR_NAME}'. Rename the folder to make this mapping explicit.")
endif()

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(${PROJECT_DIR_NAME})
