cmake_minimum_required(VERSION 3.27.1)

macro(sdk_project project_name)
project(${project_name} C ASM CXX)

set(CMAKE_EXECUTABLE_SUFFIX .elf)

if(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Linux")
    set(PYTHON_EXECUTABLE "python3")
elseif(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Windows")
    set(PYTHON_EXECUTABLE "python")
else()
    set(PYTHON_EXECUTABLE "python3")
endif()

if(DEFINED EXTRA_MODULES)
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE}
        ${SDK_BASE}/scripts/kconfig/extra_modules.py
        -m "${EXTRA_MODULES}"
        -d ${CMAKE_BINARY_DIR}
        RESULT_VARIABLE ret
    )
    # exit build process if an incorrect extra module path is given
    if(${ret} EQUAL "1")
        return()
    endif()

endif()

if(${REGEN})
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE}
        ${WORKSPACE}/config.py
        -w ${WORKSPACE}
        -c ${CMAKE_CURRENT_SOURCE_DIR}/proj.conf
        -d ${CMAKE_BINARY_DIR}
        -m
        -a ${CMAKE_CURRENT_SOURCE_DIR}
        RESULT_VARIABLE ret_config
    )

    if(${ret_config} EQUAL "1")
        message(FATAL_ERROR ret_config)
        return()
    endif()
endif()

# script reads .config file from the build directory and prints all defined
# symbols to stdout
execute_process(
    COMMAND ${PYTHON_EXECUTABLE}
    ${SDK_BASE}/scripts/kconfig/read_config.py
    -d ${CMAKE_BINARY_DIR}
    OUTPUT_VARIABLE CONFIG   
)

# convert stdout string from the script into a list 
foreach(item ${CONFIG})
    # load kconfig symbols as cmake variables
    cmake_language(EVAL CODE "set (${item})")
endforeach()

if(EXISTS ${BOARD})
    file(GLOB BOARD_CONTENTS ${BOARD}/*)
    file(COPY ${BOARD_CONTENTS} DESTINATION ${CMAKE_BINARY_DIR}/board)
else()
    message(FATAL_ERROR "Cannot find board ${BOARD}. Please check that the path to your board is correct")
endif()

if(DEFINED CONFIG_PLATFORM_MSS)
    include(${WORKSPACE}/platforms/mss/platform/CMakeLists.txt)
endif()

message(STATUS "${CONFIG_MARCH} ${CONFIG_MABI} ${CONFIG_SYSTEM_PROCESSOR}")

if(NOT("${CONFIG_MARCH}" STREQUAL ""))
    set(MARCH ${CONFIG_MARCH})
endif()

if(NOT("${CONFIG_MABI}" STREQUAL ""))
    set(MABI ${CONFIG_MABI})
endif()

if(NOT("${CONFIG_SYSTEM_PROCESSOR}" STREQUAL ""))
    set(SYS_PROC ${CONFIG_SYSTEM_PROCESSOR})
endif()

set(CMAKE_SYSTEM_PROCESSOR ${SYS_PROC})
set(CMAKE_SYSTEM_ABI ${MABI})

SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -march=${MARCH} -mabi=${MABI}")
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=${MARCH} -mabi=${MABI}")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -march=${MARCH} -mabi=${MABI}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -include autoconf.h")

message(STATUS "The toolchain used is: ${CMAKE_TOOLCHAIN_FILE}")
message(STATUS "The application name is: ${PROJECT_NAME}")
message(STATUS "The compiler flags are: ${CMAKE_C_FLAGS}")

if(NOT DEFINED CMAKE_PARALLEL_BUILD_LEVEL)
    set(CMAKE_PARALLEL_BUILD_LEVEL 1)
endif()

set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_executable(${PROJECT_NAME})

file(GLOB_RECURSE MIDDLEWARE ${CMAKE_SOURCE_DIR}/src/middleware/*.c)
file(GLOB_RECURSE MIDDLEWARE_ASSEM ${CMAKE_SOURCE_DIR}/src/middleware/*.S)
list(APPEND MIDDLEWARE ${MIDDLEWARE_ASSEM})

if(DEFINED EXTRA_MODULES)
    foreach(MODULE ${EXTRA_MODULES})
        get_filename_component(MODULE_BIN_DIR ${MODULE} NAME)
        add_subdirectory(${MODULE} ${MODULE_BIN_DIR})
    endforeach()
endif()

target_include_directories(${PROJECT_NAME} PUBLIC ${PLATFORM_HEADERS})
target_sources(${PROJECT_NAME} PUBLIC ${PLATFORM_SRC})

if(DEFINED USER_LINKER AND NOT "${USER_LINKER}" STREQUAL "")
    set(linker_script ${USER_LINKER})
endif()

execute_process(
    COMMAND ${CMAKE_C_COMPILER}
    -E
    -P
    -x c
    -I${CMAKE_BINARY_DIR}
    ${linker_script}
    OUTPUT_FILE ${CMAKE_BINARY_DIR}/generated-linker.ld
)

target_link_options(${PROJECT_NAME} PRIVATE
   -march=${CMAKE_SYSTEM_PROCESSOR} -mabi=${CMAKE_SYSTEM_ABI}
   -T${CMAKE_BINARY_DIR}/generated-linker.ld
   -nostartfiles
   -Xlinker --gc-sections
   -Wl,-Map,${PROJECT_NAME}-mine.map
   -Wa,-adhlns,${PROJECT_NAME}-mine.lst
   --specs=nano.specs
   --specs=nosys.specs
)

target_link_libraries(${PROJECT_NAME} m)

add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_OBJCOPY} -O binary ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.bin
        COMMAND ${CMAKE_OBJDUMP} --source --all-headers --demangle --line-numbers --wide ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf > ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.lst
        COMMAND ${CMAKE_SIZE} --format=sysv --totals --radix=16 ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf
)

if(CONFIG_GEN_IHEX)
    add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_OBJCOPY} -O ihex ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.hex
    )
endif()

endmacro() # project