cmake_minimum_required(VERSION 3.0)
project(WrinkleDeformer)

# Set the C++ standard you wish to use (you should match this with what Maya uses)
set(CMAKE_CXX_STANDARD 11)

# Define the path to the Maya installation. Replace this with your Maya installation path
set(MAYA_DIR "/path/to/your/maya/installation")

# Specify Maya version
set(MAYA_VERSION 2020)

# Include directories for Maya headers
include_directories(${MAYA_DIR}/include)

# Specify directories for Maya libraries
link_directories(${MAYA_DIR}/lib)

# Define source files
set(SOURCE_FILES 
    WrinkleDeformer.cpp
    # Add any additional source files here
)

# Define the target library
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

# Specify libraries to link against
target_link_libraries(${PROJECT_NAME} 
    OpenMaya
    OpenMayaAnim
    OpenMayaFX
    OpenMayaRender
    OpenMayaUI
    Foundation
    # Add any additional Maya libraries or other dependencies
)

# Define the output directory for the plugin
set_target_properties(${PROJECT_NAME} PROPERTIES 
                      LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/output")

# Set specific compile definitions and flags, if necessary
if(WIN32)
    set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".mll")
    set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "/export:initializePlugin /export:uninitializePlugin")
elseif(UNIX)
    set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "")
    set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".so")
endif()
