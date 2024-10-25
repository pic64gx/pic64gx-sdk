# PIC64GX-SDK

This repository contains the necessary tools for the [PIC64GX SDK Extension](https://marketplace.visualstudio.com/items?itemName=Microchip.pic64gx-sdk-extension)
 for Visual Studio Code.

## Prerequisites

### Requirements

#### System

- `Git`
- `Python 3.8` or later
- `CMake 3.27.1` or later

To check that your system meets the requirements:

```bash
git --version
git version 2.25.1
```

```bash
python3 --version
Python 3.8.10
```

```bash
cmake --version
cmake version 3.27.1
```

#### VS Code Extensions

- `MPLAB PIC64GX SDK`. Search for `microchip.pic64gx-sdk-extension`
- `C/C++`. Search for `ms-vscode.cpptools` in the VSCode
extension marketplace
- `Embedded Tools`. Search for `ms-vscode.vscode-embedded-tools`
in the VSCode extension marketplace
- `CMake`. Search for `twxs.cmake` in the VSCode extension
marketplace

#### Note: Python aliases

- Python can be invoked on your system using `python` (commonly on Windows), `python3` (commonly on Linux), or a custom alias.
  Pip, the Python package manager, can be invoked on your system using `pip` (commonly on Windows), `pip3` (commonly on Linux), or a custom alias.
  you can check your python version with the command `--version`. As an example:

  ```bash
  python3 --version
  Python 3.10.4
  ```

## SDK initialisation

The following commands make a workspace, enter it, and clone this repository into
a directory called `sdk`:

```bash
mkdir sdk-workspace
cd sdk-workspace
git clone https://github.com/pic64gx/pic64gx-sdk.git ./sdk
```

Enter the sdk directory to continue with initialisation:

```bash
cd ./sdk
```

### Installing Python requirements

Run the following command to install the required Python packages.

```bash
pip3 install -r scripts/requirements/requirements.txt
```

### Initialising

Run the initialisation script to install the required modules, packages, and
toolchains.

```bash
python3 scripts/init.py
```

#### Note: Git on Windows

- If you are using git that comes installed with `Git Bash`, the script above will have to be run in the Git Bash terminal.

After the initialisation script completes you can see the workspace has been
initialised. Go back into the workspace directory to begin compiling a project.

#### Note: Ninja executable on Linux

- On Linux, Ninja may be installed without execute permissions. If this is the case
  modify the permissions of `modules/ninja/ninja` and add execute permissions.

  ```bash
  chmod +x ../modules/ninja/ninja
  ```

## Workspace structure

A successfully initialized workspace will have a file hierarchy similar to:

```bash
# sdk_workspace/
.
├── boards
├── build.py
├── CMakeLists.txt
├── CMakePresets.json
├── config.py
├── Kconfig
├── modules
├── platforms
├── sdk
└── xpack-riscv-none-elf-gcc-13.2.0-2
```

## Creating a basic project

An initialised sdk workspace is equipped with everything that is required to
create, compile and debug a simple bare-metal project.

Please see the instructions in the `MPLAB PIC64GX SDK` VS Code Extension on how to create a project.

## Project structure

The SDK uses `CMake` as a project manager, to configure and compile a project.
The SDK also uses `Kconfig` to configure the embedded software.

A project has a structure, such as:

```bash
.
├── CMakeLists.txt
├── proj.conf
└── src
    └── application
        ├── hart0
        │   └── e51.c
        ├── hart1
        │   └── u54_1.c
        ├── hart2
        │   └── u54_2.c
        ├── hart3
        │   └── u54_3.c
        ├── hart4
        │   └── u54_4.c
        └── inc
            └── common.h
```

The `CMakeLists.txt` file at the top level of the project describes the
application source code and header file to include in compilation:

```cmake
cmake_minimum_required(VERSION 3.27.1)

include(${WORKSPACE}/sdk/cmake/common.cmake)

sdk_project(hello_world)

target_sources(${PROJECT_NAME} PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/application/hart1/u54_1.c
  ${CMAKE_CURRENT_SOURCE_DIR}/src/application/hart2/u54_2.c
  ${CMAKE_CURRENT_SOURCE_DIR}/src/application/hart3/u54_3.c
  ${CMAKE_CURRENT_SOURCE_DIR}/src/application/hart4/u54_4.c
  ${CMAKE_CURRENT_SOURCE_DIR}/src/application/hart0/e51.c
)

target_include_directories(${PROJECT_NAME} PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/application/
)
```

The SDK includes the PIC64GX Hardware Abstraction Layer (PIC64GX_HAL) by default in compilation. The PIC64GX_HAL is located outside of the project, in the `platforms/` directory from the workspace. This allows multiple projects to share the same embedded software without code duplication.

Adding source code files and include directories to a CMake managed project is easy. If we take the `hello_world` example above and add a directory called `foo`:

```bash
# hello_world/
.
├── CMakeLists.txt
├── proj.conf
└── src
    ├── application
    │   ├── hart0
    │   │   └── e51.c
    │   ├── hart1
    │   │   └── u54_1.c
    │   ├── hart2
    │   │   └── u54_2.c
    │   ├── hart3
    │   │   └── u54_3.c
    │   ├── hart4
    │   │   └── u54_4.c
    │   └── inc
    │       └── common.h
    └── foo
        ├── bar.c
        ├── bar.h
        ├── foo.c
        └── foo.h
```

We can add the following to the `CMakeLists.txt` file:

```cmake
# adding the following snippet
  target_sources(${PROJECT_NAME} PUBLIC
  # other files here...
   ${CMAKE_CURRENT_SOURCE_DIR}/src/foo/foo.c
   ${CMAKE_CURRENT_SOURCE_DIR}/src/foo/bar.c
  )

  target_include_directories(${PROJECT_NAME} PUBLIC
    # other include directories here...
    ${CMAKE_CURRENT_SOURCE_DIR}/src/foo/
)
```

with the above added and from our application processor files, we can include the functions from `foo` simply with:

```c
/* hart0/e51.c */

#include "foo.h"
#include "bar.h"
```

If we want to use a peripheral driver, such as UART, we can add a `Kconfig` symbol to the `proj.conf` file. By adding the symbol `CONFIG_MSS_MMUART=y` in the proj.conf
file, the SDK will include the `MSS_MMUART` driver in compilation.

```bash
# hello_world/proj.conf

CONFIG_MSS_MMUART=y
```

And from our applicaton processor files we can include the driver:

```c
/* hart0/e51.c */

#include "mss_mmuart/mss_uart.h"
```

The `Kconfig` symbols for peripheral drivers can be found in the `platforms/*` directory

## Debug a project In VS Code

The SDK uses a combination of `OpenOCD` and `GDB` to debug an applicaton.

### Note: OpenOCD on Windows

In order for `OpenOCD` to be able to communicate with the debug interface on the
PIC64GX, you will need to install drivers.
please follow the driver installation instructions for the [PIC64GX1000 Curiosity kit](https://ww1.microchip.com/downloads/aemDocuments/documents/MPU64/ProductDocuments/SupportingCollateral/PIC64GX_Curiosity_Kit_User_Guide.pdf)
before running a debug session

### Note: OpenOCD on Linux

To use OpenOCD without sudo privileges on Linux, from the sdk_workspace:

```bash
# copy udev rules for OpenOCD

sudo cp modules/debug/openocd-0.12.0-4/openocd/contrib/60-openocd.rules /etc/udev/rules.d/

sudo udevadm control --reload
```

`.vscode/launch.json` contains launch configurations for debugging a project
in `VS Code`. Press `Ctrl+Shift+D` to open the `Debug and Run`
panel. From the drop-down menu select the debug configuration to use depending
on the type of project and debugger, then run the deubg configuration. You
will be prompted to enter the path to the `.elf` file, this is a relative path
from the base directory of the SDK.

### Run Project in Renode Emulation

Projects in this development environment can be run using the Renode emulation
tool. Renode can be launched by selecting the `debug-renode` option in
the Debug and Run drop-down menu as described above. In addition to specifying
the path to the .elf file, select the board platform file that represents the
target hardware from the menu.

More information about using Renode can be found on
[https://renode.readthedocs.io](https://renode.readthedocs.io)
