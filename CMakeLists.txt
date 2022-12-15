cmake_minimum_required(VERSION 3.12)
# CMake version requirements:
#  - 3.11+ is required for FetchContent module
#  - 3.12+ is required for Python3 module

if(NOT PYMAD_VERSION)
    message(FATAL_ERROR "PYMAD_VERSION is not set. Pass it -DPYMAD_VERSION=1.2.3 in a command line")
endif()

set(PYMAD_PYTHON_MODULE_NAME "pymad" CACHE STRING "Name of the C extension module file")

if(WIN32)
    set(PYMAD_PYTHON_MODULE_EXT ".pyd" CACHE STRING "Extension of the C extension module file")
else()
    set(PYMAD_PYTHON_MODULE_EXT ".so" CACHE STRING "Extension of the C extension module file")
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
    OUTPUT_NAME "${PYMAD_PYTHON_MODULE_NAME}"
    SUFFIX "${PYMAD_PYTHON_MODULE_EXT}"
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

# On Windows, it is required to link to the Python libraries
if(WIN32)
    target_link_libraries(${PROJECT_NAME} ${Python3_LIBRARIES})
endif()


# -----------------------------------------------------
# "libmad" dependency
# -----------------------------------------------------
option(PYMAD_USE_SYSTEM_LIBMAD "Link with libmad, which is installed in system, rather than downloading it from github" OFF)


if(PYMAD_USE_SYSTEM_LIBMAD)
    target_link_libraries(${PROJECT_NAME} PRIVATE mad)
else()

    set(PYMAD_LIBMAD_REPO_URL "https://github.com/miarec/libmad" CACHE STRING "Git repository URL, from where to fetch the libmad library")
    set(PYMAD_LIBMAD_REPO_TAG "master" CACHE STRING "Git repository tag/branch to fetch the libmad project")

    include(FetchContent)

    FetchContent_Declare(
        mad
        GIT_REPOSITORY "${PYMAD_LIBMAD_REPO_URL}"
        GIT_TAG "${PYMAD_LIBMAD_REPO_TAG}"
    )
    FetchContent_MakeAvailable(mad)


    # FetchContent_GetProperties(libmad)
    # if(NOT libmad_POPULATED)
        # FetchContent_Populate(libmad)
        # add_subdirectory(
            # "${libmad_SOURCE_DIR}"
            # "${libmad_BINARY_DIR}"
        # )
    # endif()

    message(STATUS "mad_SOURCE_DIR=${mad_SOURCE_DIR}, mad_BINARY_DIR=${mad_BINARY_DIR}")

    target_link_libraries(${PROJECT_NAME} PRIVATE mad)

endif()


# set(PYMAD_PYTHON_C_MODULE_NAME "_pymad" CACHE STRING "Name of the C extension module file")