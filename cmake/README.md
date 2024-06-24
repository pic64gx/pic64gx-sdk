## `preload.cmake`
This file is used by the build script to pre-populate the cache with a
variable pointing to the version of ninja needed for the host's operating
system.

## `cross-compiler-gcc-tc.cmake`
This file sets up the toolchain. It expects the toolchain to be located in the
base directory of this repository in a directory called 
`xpack-riscv-none-elf-gcc-13.2.0-2`. The path to this file is passed to CMake
with the `CMAKE_TOOLCHAIN_FILE` argument.

## `common.cmake`
This file contains functions that are common between all bare metal example
projects. The `include(${SDK_BASE}/cmake/common.cmake)` function found in the
`CMakeLists.txt` file in each example project loads in this file. The path to
this file is passed to CMake with the `CMAKE_MODULE_PATH` argument. 