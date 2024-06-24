set(CMAKE_SHARED_LIBRARY_LINK_C_FLAGS "")
set(CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS "")

if(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Linux")
	set(CMAKE_MAKE_PROGRAM ${WORKSPACE}/modules/ninja/ninja CACHE FILEPATH "")
elseif(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Windows")
	set(CMAKE_MAKE_PROGRAM ${WORKSPACE}/modules/ninja/ninja.exe CACHE FILEPATH "")
endif()

set(CMAKE_GENERATOR "Ninja" CACHE INTERNAL "" FORCE)

SET(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_VERSION 1)
SET(CMAKE_CROSSCOMPILING TRUE)
set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_EXECUTABLE_SUFFIX ".elf")

# variable that is used for the toolchain
set(riscv_toolchain_base ${WORKSPACE}/xpack-riscv-none-elf-gcc-13.2.0-2)

# here is the target environment located
set(CMAKE_FIND_ROOT_PATH ${riscv_toolchain_base})

set(riscv_toolchain_bin_path ${riscv_toolchain_base}/bin)
set(riscv_toolchain_prefix riscv-none-elf)

set(CMAKE_LIBRARY_ARCHITECTURE ${riscv_toolchain_bin_path})

if(UNIX)
    set(executable_extension)
elseif(WIN32)
    set(executable_extension .exe)
endif()
    
# which compilers to use for C and C++
set(CMAKE_C_COMPILER ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-gcc${executable_extension})
set(CMAKE_CXX_COMPILER ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-g++${executable_extension})
set(CMAKE_AR ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-ar${executable_extension})
set(CMAKE_ASM_COMPILER ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-gcc${executable_extension})

# We must set the OBJCOPY setting into cache so that it's available to the
# whole project. Otherwise, this does not get set into the CACHE and therefore
# the build doesn't know what the OBJCOPY filepath is
set(CMAKE_OBJCOPY ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-objcopy${executable_extension} CACHE FILEPATH "The toolchain objcopy command " FORCE )
set(CMAKE_OBJDUMP ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-objdump${executable_extension} CACHE FILEPATH "The toolchain objdump command " FORCE )
set(CMAKE_SIZE ${riscv_toolchain_bin_path}/${riscv_toolchain_prefix}-size${executable_extension} CACHE FILEPATH "The toolchain size command " FORCE )

set(CMAKE_ASM_SOURCE_FILE_EXTENSIONS S)
# adjust the default behaviour of the FIND_XXX() commands:
# search headers and libraries in the target environment, search
# programs in the host environment
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -O2 -fno-builtin-printf")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mcmodel=medany")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -msmall-data-limit=8")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mstrict-align")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mno-save-restore")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mexplicit-relocs")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fmessage-length=0")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsigned-char")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -ffunction-sections")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fdata-sections")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g3")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu11")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wstrict-prototypes")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wbad-function-cast")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wl,-allow-multiple-definition")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${EXTRA_C_FLAGS}")

set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -mcmodel=medany")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -msmall-data-limit=8")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -mstrict-align")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -mno-save-restore")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -O0")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -fmessage-length=0")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -fsigned-char")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -ffunction-sections")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -fdata-sections")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -g3")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -std=gnu11")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -Wstrict-prototypes")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -Wbad-function-cast")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -x assembler-with-cpp")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${EXTRA_ASM_FLAGS}")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mcmodel=medany")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -msmall-data-limit=8")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mstrict-align")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mno-save-restore")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fmessage-length=0")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsigned-char")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ffunction-sections")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fdata-sections")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g3")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fabi-version=13")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-use-cxa-atexit")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-threadsafe-statics")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,-allow-multiple-definition")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${EXTRA_CXX_FLAGS}")