cmake_minimum_required(VERSION 3.0)

# Project name
project(textLocator)

# Set C++11 standard
set(CMAKE_CXX_STANDARD 11)

# Set Maya path
set(MAYA_PATH "/usr/autodesk/maya2022")

# Add include directories
include_directories(${MAYA_PATH}/include)

# Add library directories
link_directories(${MAYA_PATH}/lib)

# Add source files
set(SOURCES TextLocator.cpp)

# Create shared library
add_library(${PROJECT_NAME} SHARED ${SOURCES})

# Link Maya libraries
target_link_libraries(${PROJECT_NAME} OpenMaya Foundation)

# Set output directory
set_target_properties(${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# Set output name
set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "")
