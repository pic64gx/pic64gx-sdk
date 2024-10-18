cmake_minimum_required(VERSION 3.27.1)

# when cmake functions are overridden the original version of the function can
# be called by prepending the function call with an underscore
# override the cmake project() function to a noop

# Trick to temporarily redefine project(). When functions are overridden in 
# CMake, the originals can still be accessed using an underscore prefixed 
# function of the same name. The following lines make sure that __project  calls
# the original project(). See https://cmake.org/pipermail/cmake/2015-October/061751.html.

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

if(DEFINED CONFIG_PLATFORM_MSS)
    set(CONFIG_PLATFORM mss)
    set(SYS_PROC rv64imafdc_zicsr)
    set(MARCH rv64imafdc_zicsr_zifencei)
    set(MABI lp64d)
    set(HEX_FORMAT ihex)
elseif(DEFINED CONFIG_PLATFORM_MIV)
    set(CONFIG_PLATFORM miv)
    set(SYS_PROC rv32im_zicsr)
    set(MARCH rv32im_zicsr_zifencei)
    set(MABI ilp32)
    set(HEX_FORMAT ihex)
elseif(DEFINED CONFIG_PLATFORM_MPS)
    set(SYS_PROC rv64imafc_zicsr)
    set(MARCH rv64imafc_zicsr)
    set(MABI lp64f)
    set(HEX_FORMAT ihex)
elseif(DEFINED CONFIG_PLATFORM_VPB)
    set(CONFIG_PLATFORM vpb)
    set(SYS_PROC rv64imafc_zicsr)
    set(MARCH rv64imafc_zicsr_zifencei_zve32f_zfh)
    set(MABI lp64f)
    set(HEX_FORMAT verilog)
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

if(EXISTS ${BOARD})
    file(GLOB BOARD_CONTENTS ${BOARD}/*)
    file(COPY ${BOARD_CONTENTS} DESTINATION ${CMAKE_BINARY_DIR}/board)
else()
    message(FATAL_ERROR "Cannot find board ${BOARD}. Please check that the path to your board is correct")
endif()

# assemble headers and sources based on the chosen platform
if(DEFINED CONFIG_PLATFORM_MSS)
    # including the CMakeLists.txt file from platform exposes the MSS_DRIVERS and
    # MIV_DRIVERS lists to the build system
    add_subdirectory(${WORKSPACE}/platforms/mss/platform ${CMAKE_BINARY_DIR}/platform)

    set(linker_script_path ${WORKSPACE}/platforms/mss/platform/platform_config_reference/linker/)

    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} 
        ${WORKSPACE}/platforms/mss/platform/soc_config_generator/mpfs_configuration_generator.py 
        ${CMAKE_BINARY_DIR}/board/fpga_design/design_description/ 
        ${CMAKE_BINARY_DIR}/board
    )

    list(APPEND headers
        ${CMAKE_SOURCE_DIR}/src/application/
        ${WORKSPACE}/platforms/mss/platform
        ${WORKSPACE}/platforms/mss/platform/mpfs_hal/
        ${CMAKE_BINARY_DIR}/board/
        ${CMAKE_BINARY_DIR}/board/fpga_design_config/
        ${CMAKE_BINARY_DIR}/board/platform_config/
        ${WORKSPACE}/platforms/mss/platform/platform_config_reference/
        ${CMAKE_BINARY_DIR}
    )

    if(${CONFIG_MEMORY} MATCHES "ddr")
        list(APPEND headers
            ${CMAKE_BINARY_DIR}/board/platform_config_ddr/
            ${CMAKE_BINARY_DIR}/board/platform_config_ddr/mpfs_hal_config/    
        )
    else()
        list(APPEND headers
            ${CMAKE_BINARY_DIR}/board/platform_config/
            ${CMAKE_BINARY_DIR}/board/platform_config/mpfs_hal_config/    
        )
    endif()

    set(sources
        ${HAL}
        ${MPFS_HAL}
        ${ASSEM}
        ${MSS_DRIVERS}
        ${MIDDLEWARE}
    )

    if(${CONFIG_MEMORY} MATCHES "envm")
        set(linker_script ${linker_script_path}/mpfs-envm.ld)
    elseif(${CONFIG_MEMORY} MATCHES "scratchpad")
        set(linker_script ${linker_script_path}/mpfs-lim-lma-scratchpad-vma.ld)
    elseif(${CONFIG_MEMORY} MATCHES "lim")
        set(linker_script ${linker_script_path}/mpfs-lim.ld)
    elseif(${CONFIG_MEMORY} MATCHES "ddr")
        set(linker_script ${linker_script_path}/mpfs-ddr-loaded-by-boot-loader.ld)
    else()
        set(linker_script ${linker_script_path}/mpfs-lim.ld)
    endif()

elseif(DEFINED CONFIG_PLATFORM_MIV)
    add_subdirectory(${WORKSPACE}/platforms/miv/platform ${CMAKE_BINARY_DIR}/platform)

    set(linker_script_path ${WORKSPACE}/platforms/miv/platform/platform_config_reference/linker/)

    list(APPEND headers
        ${WORKSPACE}/platforms/miv/platform
        ${WORKSPACE}/platforms/miv/platform/miv_rv32_hal/
        ${CMAKE_BINARY_DIR}/board/
        ${CMAKE_BINARY_DIR}/board/platform_config/
        ${CMAKE_BINARY_DIR}
    )

    set(sources
        ${HAL}
        ${MIV_RV32_HAL}
        ${ASSEM}
        ${MIV_DRIVERS}
        ${MIDDLEWARE}
    )

    set(linker_script ${linker_script_path}/miv-rv32-ram.ld)

elseif(DEFINED CONFIG_PLATFORM_MPS)
    add_subdirectory(${WORKSPACE}/platforms/mps/platform ${CMAKE_BINARY_DIR}/platform)

    set(linker_script_path ${WORKSPACE}/platforms/mps/platform/platform_config_reference/linker/)

    list(APPEND headers
        ${WORKSPACE}/platforms/mps/platform
        ${WORKSPACE}/platforms/mps/platform/monp_hal/
        ${CMAKE_BINARY_DIR}/board/
        ${CMAKE_BINARY_DIR}
    )

    set(sources
        ${HAL}
        ${MONP_HAL}
        ${ASSEM}
        ${MPS_DRIVERS}
        ${MIDDLEWARE}
    )

    set(linker_script ${linker_script_path}/monp_hal_ram.ld)

elseif(DEFINED CONFIG_PLATFORM_VPB)
    add_subdirectory(${WORKSPACE}/platforms/vpb/platform ${CMAKE_BINARY_DIR}/platform)

    set(linker_script ${WORKSPACE}/platforms/vpb/platform/platform_config_reference/linker/vpb_vsram.ld)

    list(APPEND headers
        ${WORKSPACE}/platforms/vpb/platform
        ${WORKSPACE}/platforms/vpb/platform/vpb_hal/
        ${CMAKE_BINARY_DIR}/board/
        ${CMAKE_BINARY_DIR}
    )

    set(sources
        ${HAL}
        ${VPB_HAL}
        ${ASSEM}
        ${VPB_DRIVERS}
        ${MIDDLEWARE}
    )
endif()

if(DEFINED EXTRA_MODULES)
    foreach(MODULE ${EXTRA_MODULES})
        get_filename_component(MODULE_BIN_DIR ${MODULE} NAME)
        add_subdirectory(${MODULE} ${MODULE_BIN_DIR})
    endforeach()
endif()

target_include_directories(${PROJECT_NAME} PUBLIC ${headers})
target_sources(${PROJECT_NAME} PUBLIC ${sources})

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
        COMMAND ${CMAKE_OBJCOPY} -O ${HEX_FORMAT} ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.hex
        COMMAND ${CMAKE_OBJDUMP} --source --all-headers --demangle --line-numbers --wide ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf > ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.lst
        COMMAND ${CMAKE_SIZE} --format=sysv --totals --radix=16 ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf
)

endmacro() # project