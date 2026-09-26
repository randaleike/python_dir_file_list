# specify the cmake minimum version
cmake_minimum_required(VERSION 3.10)
get_filename_component(ProjectId ${CMAKE_CURRENT_SOURCE_DIR} NAME)

# set the project name
project(${ProjectId}
        VERSION 0.4.3
        SPDX_LICENSE "MIT"
        DESCRIPTION "Directory/File List Generation"
        HOMEPAGE_URL "https://github.com/randaleike/python_dir_file_list")

set(PROJECT_AUTHOR grocsoftware)
set(PROJECT_EMAIL "support@grocsoftware.com")

find_package(Python3 REQUIRED)
#find_package(PythonInterp REQUIRED)
#find_package(PythonLibs REQUIRED)

file(REMOVE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake)
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "# Project clean project generated files script\n")

file(REMOVE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake)
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "# Project clean temporary files script\n")

####
# Python source
####
set(PYTHON_SRC_DIR
    ${CMAKE_CURRENT_LIST_DIR}/src
    )

set(PYTHON_BASE_SRC_DIR
    ${PYTHON_SRC_DIR}/dirscan_grocsoftware
    )

set(PYTHON_SRC
    ${PYTHON_BASE_SRC_DIR}/scan.py
    )


####
# Python test source
####
set(PYTHON_TEST_DIR
    ${CMAKE_CURRENT_LIST_DIR}/tests
    )

set(PYTHON_TEST_SRC
    ${PYTHON_TEST_DIR}/test_scan.py
    )


foreach(DIRNAME IN LISTS PYTHON_SRC_DIR PYTHON_TEST_DIR)
    file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE_RECURSE ${DIRNAME}/__pycache__/)\n")
endforeach()

# Unittests
message ("Python base = ${PYTHON_BASE_DIR}")
set(DIR_INIT_IN ${PYTHON_TEST_DIR}/dir_init.py.in)
set(DIR_INIT_OUT ${PYTHON_TEST_DIR}/dir_init.py)
configure_file(${DIR_INIT_IN} ${DIR_INIT_OUT} @ONLY)
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "file(REMOVE ${DIR_INIT_OUT})\n")

enable_testing()

add_custom_target(${PROJECT_NAME}-unittest ALL
    DEPENDS ${PYTHON_SRC} ${PYTHON_TEST_SRC}
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND ${Python3_EXECUTABLE} -m coverage run -m unittest discover -s tests/
    COMMAND ${Python3_EXECUTABLE} -m coverage html --omit dir_init.py,test_*.py --fail-under=95
    COMMENT "Run Python ${PROJECT_NAME} Unittest"
)
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE ${CMAKE_CURRENT_LIST_DIR}/tests/.coverage)\n")
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE ${CMAKE_CURRENT_LIST_DIR}/.coverage)\n")
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE_RECURSE ${CMAKE_CURRENT_LIST_DIR}/htmlcov/)\n")
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE_RECURSE ${CMAKE_CURRENT_LIST_DIR}/tests/htmlcov/)\n")

####
# doxygen generation
####
find_package(Doxygen
             REQUIRED dot
             OPTIONAL_COMPONENTS mscgen dia)

# ReadMe config
set(README_IN ${CMAKE_CURRENT_LIST_DIR}/setup_files/README.md.in)
set(README_OUT ${CMAKE_CURRENT_LIST_DIR}/README.md)
configure_file(${README_IN} ${README_OUT} @ONLY)
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "file(REMOVE ${README_OUT})\n")

# Update Doxygen config
set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_LIST_DIR}/doc)
set(DOXYGEN_IN ${CMAKE_CURRENT_LIST_DIR}/setup_files/Doxyfile.in)
set(DOXYGEN_OUT ${CMAKE_CURRENT_LIST_DIR}/Doxyfile)
configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "file(REMOVE ${DOXYGEN_OUT})\n")

if ((CMAKE_BUILD_TYPE MATCHES "^[Rr]elease") AND DOXYGEN_FOUND)
    message("Master Doxygen build enabled")

    # Add Doxygen target
    add_custom_target(${PROJECT_NAME}-builddoc
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Generating API documentation with Doxygen"
        DEPENDS ${PYTHON_SRC}
        VERBATIM )

endif()
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "file(REMOVE_RECURSE ${CMAKE_CURRENT_LIST_DIR}/doc)\n")

####
# python package generation
####
if (CMAKE_BUILD_TYPE MATCHES "^[Rr]elease")
    # Update pyproject
    set(PYPROJECT_IN ${CMAKE_CURRENT_LIST_DIR}/setup_files/pyproject.toml.in)
    set(PYPROJECT_OUT ${CMAKE_CURRENT_LIST_DIR}/pyproject.toml)
    configure_file(${PYPROJECT_IN} ${PYPROJECT_OUT} @ONLY)
    message("Master Python package build enabled")

    add_custom_target(${PROJECT_NAME}-package
        COMMAND ${Python3_EXECUTABLE} -m build
        WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
        COMMENT "Python Package build"
        DEPENDS ${PYTHON_SRC}
        VERBATIM )
endif()
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE_RECURSE ${CMAKE_CURRENT_LIST_DIR}/${PROJECT_NAME}_${PROJECT_AUTHOR}.egg-info)\n")
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake "file(REMOVE_RECURSE ${CMAKE_CURRENT_LIST_DIR}/dist)\n")
file(APPEND ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake "file(REMOVE ${PYPROJECT_OUT})\n")

####
# package build cleanup
####
add_custom_target(${PROJECT_NAME}-clean
    COMMENT "Build cleanup"
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake
    )

add_custom_target(${PROJECT_NAME}-reset
    COMMENT "Build cleanup, Reset generated files"
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-clean-tempfiles.cmake
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-reset-generated.cmake
    )
