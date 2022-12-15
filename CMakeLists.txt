cmake_minimum_required(VERSION 3.12)

if(NOT PYMAD_VERSION)
    message(FATAL_ERROR "PYMAD_VERSION is not set. Pass it -DPYMAD_VERSION=1.2.3 in a command line")
endif()

project(pymad 
    LANGUAGES C
    VERSION "${PYMAD_VERSION}"
)

set(CMAKE_C_EXTENSIONS OFF)

message(STATUS "Building ${PROJECT_NAME} python extension version ${PROJECT_VERSION}...")

if(NOT PYTHON_VERSION)
    message(FATAL_ERROR "PYTHON_VERSION is not set. Pass it -DPYTHON_VERSION=3.8 in a command line")
endif()
message(STATUS "Searching for Python ${PYTHON_VERSION}...")
find_package (Python3 
    ${PYTHON_VERSION} EXACT
    COMPONENTS Interpreter Development 
    REQUIRED
)
message(STATUS "Found Python ${Python3_VERSION} at ${Python3_EXECUTABLE} (include_dirs=${Python3_INCLUDE_DIRS})")

# ---------------------------------------------------------------
# Define library (python extension) "pymad.[so|pyd]"
# ---------------------------------------------------------------
add_library(pymad SHARED
    src/pymadfile.c
    src/madmodule.c
)

set_target_properties(${PROJECT_NAME} PROPERTIES
  POSITION_INDEPENDENT_CODE ON                 # enable "-fPIC" (required for a library)
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    PREFIX ""
    OUTPUT_NAME "mad"
    LINKER_LANGUAGE C
)

# Tell the compiler/linker where to find Python.h and library files
set_target_properties(${PROJECT_NAME} PROPERTIES 
    INCLUDE_DIRECTORIES "${Python3_INCLUDE_DIRS}"
    LINK_DIRECTORIES "${Python3_LIBRARY_DIRS}"
)

target_compile_options(${PROJECT_NAME}
    PRIVATE
        -DVERSION="${PROJECT_VERSION}"
)

if(WIN32)
    set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES
        SUFFIX ".pyd"
    )
endif()

# -----------------------------------------------------
# "libmad" dependency
# -----------------------------------------------------
target_link_libraries(${PROJECT_NAME} PRIVATE mad)

# On Windows, it is required to link to the Python libraries
if(WIN32)
    target_link_libraries(${PROJECT_NAME} ${Python3_LIBRARIES})
endif()

# set(PYMAD_PYTHON_C_MODULE_NAME "_pymad" CACHE STRING "Name of the C extension module file")