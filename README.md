# PIC64GX-SDK

This repository contains tooling required for the Visual Studio Code
PIC64GX SDK Extension.

## Prerequisites

### Requirements

- Git 2.32.0.windows.1 or later if using Windows
- Git 2.34.1 or later if using Linux
- Python 3.8 or later
- CMake 3.27.1 or later
- C/C++ VSCode extension. Search for `ms-vscode.cpptools` in the VSCode
extension marketplace
- Embedded Tools VSCode extension. Search for `ms-vscode.vscode-embedded-tools`
in the VSCode extension marketplace
- CMake VSCode extension. Search for `twxs.cmake` in the VSCode extension
marketplace

### Tool Aliases

Python may be invoked on your system by calling `python` (usually Windows),
`python3` (usually Linux), or a custom alias.

Pip, the python package manager may be invoked on your system by calling `pip`
(usually Windows), `pip3` (usually Linux), or a custom alias.

## Initialisation Instructions

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

### Installing Python Packages

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

On Linux Ninja may be installed without execute permissions. If this is the case
modify the permissions of `modules/ninja/ninja` and add execute permissions.

```bash
chmod +x ../modules/ninja/ninja
```

If on Windows and using git that comes installed with Git Bash this script
will have to be run in the Git Bash terminal.

After the initialisation script completes you can see the workspace has been
initialised. Go back into the workspace directory to begin compiling a project.

### Workspace Structure

When initialised, the workspace will contain folders, such as `modules/debug` where `OpenOCD` is located and `xpack-riscv-none-elf-gcc-*`, where the RISC-V toolchain is located.

### Debugging A Project In VSCode

`sdk/.vscode/launch.json` contains launch configurations for debugging a project
in Microsoft's Visual Studio Code. You can copy the `.vscode` directory to the
workspace folder to use these. Press `Ctrl+Shift+D` to open the Debug and Run
panel. From the drop-down menu select the debug configuration to use depending
on the type of project and debugger, then run the deubg configuration. You
will be prompted to enter the path to the .elf file, this is a relative path
from the base directory of the SDK.

### Building A Project For Renode Emulation

Projects in this development environment can be run using the Renode emulation
tool. Renode can be launched by selecting the `debug-renode` option in
the Debug and Run drop-down menu as described above. In addition to specifying
the path to the .elf file, select the board platform file that represents the
target hardware from the menu.

More information about using Renode can be found on
[https://renode.readthedocs.io](https://renode.readthedocs.io)
