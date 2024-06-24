cmake_minimum_required(VERSION 3.27.1)

include(${WORKSPACE}/sdk/cmake/common.cmake)

project(${NAME})

target_sources(${PROJECT_NAME} PUBLIC
${PROJECT_SOURCE_FILES}
${ADDITIONAL_SOURCE_FILES}
)

target_include_directories(${PROJECT_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/application/
${ADDITIONAL_INCLUDE_DIRECTORIES}
)