# PIC64GX Configurator - VSCode Extension

## End User Quick Start Guide

This guide walks you through using the PIC64GX Configurator to create and manage AMP memory configurations, peripherals, and device tree overlays for Microchip PIC64GX platform, supporting both Zephyr and Linux environments.

**Prefer a guided step-by-step walkthrough example flow?**  
For a complete and specific example flow (project creation → AMP configuration → generated outputs), see:  [**PIC64GX Configurator – Example User Flow**](./example-configuration-flow.md)



## Prerequisites

Before using the PIC64GX Configurator:

- **Device Tree Compiler (`dtc`)** available in your system PATH:
  - On **Windows**, install `dtc` (e.g., via MSYS2 or a precompiled binary)
  - On **Linux**, install using your package manager (`sudo apt install device-tree-compiler`)

- The extension uses `dtc` to:
  - Validate DTS/DTSI syntax
  - Compile `.dtso` overlays into `.dtbo` binary files automatically during generation

> **System-level DTS usage**
>  
> The PIC64GX Configurator uses bundled system-level DTS/DTSI files by default.
> Custom system-level DTS/DTSI files are not supported in this version.

---

## 1. System-level DTS Configuration

The PIC64GX Configurator uses a **bundled, system-level DTS/DTSI configuration**
provided with the extension for the **PIC64GX Curiosity Kit**.

At this time, **custom system-level DTS/DTSI selection is not supported**.
This restriction is intentional, to ensure that only validated and supported
platform configurations are used.

### Default Behavior

- A default PIC64GX Curiosity Kit **system-level DTS** is always used
- The corresponding PIC64GX **SoC DTSI** files are included automatically
- No user action is required to select or configure these files

### MANIFEST File (Auto-managed)

When a project is created, the Configurator automatically creates and manages
a `MANIFEST` file in the project directory.

This file is used internally to track:
- Generated output paths
- Project metadata required to reopen the project

> The `MANIFEST` file is **not intended to be edited manually** to change
> the system-level DTS configuration in the current version.

### Future Support

Support for custom system-level DTS/DTSI files may be reintroduced in future
versions once validation and compatibility guarantees are in place.

### Default System-level DTS and DTSI Files (Bundled with the Extension)

The PIC64GX Configurator automatically uses the default PIC64GX device tree
files bundled within its installation directory.

These files define the supported system-level configuration for the
PIC64GX Curiosity Kit and are used for all projects created with the tool.

| Platform | Default System-level DTS/DTSI Location |
|-----------|---------------------------------------|
| **Linux** | `~/.vscode/extensions/microchip.pic64gx-configurator-<version>/assets/pic64gx-curiosity-kit/` |
| **Windows** | `%USERPROFILE%\.vscode\extensions\microchip.pic64gx-configurator-<version>\assets\pic64gx-curiosity-kit\` |

**Included files:**
- PIC64GX Curiosity Kit **system-level DTS**
- PIC64GX **SoC DTSI** definitions

---

## 2. Create a New Project

1. Click **"Create New Project"** from the button provided  
2. Select the folder that will contain your project's files

The Configurator uses a **validated, bundled system-level DTS/DTSI configuration**
for the PIC64GX Curiosity Kit. No system-level DTS selection is required or
available during project creation.

The tool will:

- Automatically create and manage a `MANIFEST` file in the selected folder
- Use the bundled PIC64GX Curiosity Kit **system-level DTS/DTSI configuration**
- Read and parse the system-level DTS and all included DTSI files
- Validate that the system-level DTS is compatible with PIC64GX:
  - Checks for:  
    `compatible = "microchip,pic64gx-curiosity-kit", "microchip,pic64gx"`
  - If not found, an error will be displayed
- Convert the DTS/DTSI structure into **temporary YAML configuration files**
  stored under a hidden `.temp` folder for internal use:
  - `.temp/context_a.yaml`
  - `.temp/context_b.yaml`
  - `.temp/global.yaml`
- Load the YAML configuration into the UI (DDR, L2, and Peripherals views)
- Keep the `.temp` folder synchronized with the UI configuration until the
  **Generate** step

> **Default configuration**
>
> Project creation always starts from the validated, bundled PIC64GX Curiosity Kit
> system-level DTS/DTSI configuration. Custom system-level DTS selection is not
> supported in the current version.

### DTSI Handling

- The Configurator supports **multi-include DTSI structures**
- All included DTSI files are merged into a unified device tree representation
- `#include` tags and relative paths are resolved automatically, including:
  - Nested includes (e.g. `#include "soc/pic64gx_peripherals.dtsi"`)
  - Header includes (e.g. `#include "dt-bindings/clock/pic64gx.h"`)
- DTSI paths are resolved relative to the bundled system-level DTS/DTSI layout

Note: All DTS and DTSI parsing is performed against the bundled system-level
configuration provided with the extension.

> The `.temp` folder is automatically removed after a successful **Generate**
> operation.


---

## 3. Open an Existing Project

To reopen a previously created PIC64GX Configurator project:

1. Click **"Open Project"** from the Configurator panel  
2. Select a folder that contains a valid `MANIFEST` file

The Configurator will:

- Read the `MANIFEST` file in the selected directory
- Restore all project metadata required to reopen the project
- Load the previously generated `global.yaml` configuration file
- Parse the YAML file and reconstruct the UI state, including:
  - DDR memory regions
  - AMP configuration
  - Processor (hart) assignments
  - Peripheral assignments and context ownership
- Restore the internal `.temp` working state to allow further edits
- Validate the restored configuration before allowing generation

> **Project consistency**
>
> Opening a project always uses the previously generated YAML configuration file, based on the same bundled system-level DTS/DTSI configuration that was used when
> the project was created. The system-level DTS configuration is not reselected
> or modified when reopening a project.


### MANIFEST File Role

The `MANIFEST` file acts as the single source of truth for reopening a project.
It is created, if doesn't exist, and managed automatically by the Configurator and is used to:

- Locate generated output files
- Restore project configuration state
- Ensure the project can be reopened consistently across sessions

> The `MANIFEST` file is not intended to be edited manually.
> Manual changes may result in an invalid or unrecoverable project state.

### Validation on Open

When a project is opened:

- All restored configuration values are validated
- Any invalid or inconsistent configuration is shown in the UI as an error or warning
- Generation is blocked until all blocking validation errors are resolved

> Validation rules applied during project opening are the same rules enforced
> during normal configuration and generation.


---

## 4. Configure DDR Memory Regions

The **DDR view** allows you to define and manage DDR memory regions for each execution context. Memory regions and values are initially imported from the bundled system-level DTS/DTSI files and are later refined through the UI.

DDR configuration affects:
- Linux and Zephyr memory layout
- AMP memory separation
- Reserved memory regions required for inter-context communication

### DDR Table Fields

| Field        | Description |
|--------------|-------------|
| **Name**     | Required and must be unique. Cannot contain spaces or start with a number.|
| **Size**     | Supports B / KB / MB / GB / TB units with automatic conversion. Displayed with comma separators (e.g. `1,073,741,824`) |
| **Address**  | Base address in hex (placeholder: `0x...`). Must be in the 32–38 bit range |
| **Context**  | `Context A`, `Context B`, or `Both` (visible only when AMP is enabled) |
| **Type**     | `Main memory` or `Reserved memory` (visible only when AMP is enabled) |

> DDR regions are validated dynamically using the address ranges parsed from
> the system-level DTS/DTSI files. No hardcoded address limits are used.

--- 
### Logic and Behavior

- **If AMP is enabled**:
  - `Context` and `Type` columns become visible
  - **Type = Reserved memory** → allows `Both` in Context
  - **Type = Main memory** → restricts Context to `A` or `B` only
  - Peripherals sections become visible

- **If AMP is disabled**:
  - Context is auto-set to `Context A`
  - Context, Type fields are hidden

### Validations

- **Names**: Must be unique, without spaces or beginning with a number.  
- **Address**: Hex format (`0x...`), validated within the **36-bit physical DDR range** (`≤ 0x0FFFFFFFFF`), and must not duplicate existing regions.  
- **Size**: Minimum 32 bytes, supports B/KB/MB/GB/TB with auto-conversion and rounding (e.g., 1024 MB = 1 GB).  
  - Allows regions smaller that 1 MB (e.g., 256 KB).  
  - Ensures `(base + size - 1)` remains within the **DTS/DTSI defined DDR size**.  
- **Overlap Check**: Prevents overlapping regions, and allows end-aligned boundaries.  
- **AMP Rules**:  
  - **Reserved** = `Both` contexts allowed to be checked.  
  - **Main** = Only Context A or B.  
  - If AMP is disabled, Context A is enforced automatically.  
- **Dynamic Bounds**: Address and size validations use the parsed DTS/DTSI ranges (no hardcoded values).  
- **UI Feedback**:  
  - Errors and warnings displayed dynamically.  
  - Empty DDR tables show helper messages to guide users.  
- **Consistency**: All validations are automatically re-checked also before **Generate** to prevent invalid output files.   

---

## 5. Configure Peripherals, Context OS, and Processor Assignment

The **Peripherals view** is the central place where you define:

- Which operating system runs on each context
- Which processor cores (harts) belong to each context
- Which peripherals are enabled for each context
- Which UART is considered the **stdout console** for Linux and Zephyr

This configuration directly drives how CPU nodes, IHC nodes, chosen nodes,
stdout configuration, and peripheral status are written into the generated
Linux `.dtso` and Zephyr `.overlay` files.

### Context Configuration (Linux / Zephyr)

At the top of the view, the **Context Configuration** table allows selecting
which OS runs on each context.

| Context | Linux | Zephyr |
|--------|-------|--------|
| Context A | ✔ | |
| Context B | | ✔ |

#### Rules

- Each context can run **either Linux or Zephyr**
- When AMP is disabled, only **Context A** is active
- When AMP is enabled, both contexts must have a valid OS selection
- The OS selection determines:
  - Which type of overlay is generated (`.dtso` or `.overlay`)
  - How memory nodes are written
  - How the `chosen` node is generated
  - Which peripherals are allowed (Zephyr filtering)


### Processor Initiators (Hart Assignment)

The **Processor Initiators** table defines which U54 harts belong to each context.

| Processor | Context A | Context B |
|-----------|-----------|-----------|
| u54_1 | ☐ | ☐ |
| u54_2 | ☐ | ☐ |
| u54_3 | ☐ | ☐ |
| u54_4 | ☐ | ☐ |

#### Rules

- A hart can belong to **only one context**
- When AMP is disabled, all harts belong to **Context A**
- When AMP is enabled, at least **one hart should be assigned** to each active context
- The hart mapping determines:
  - CPU node `status = "okay"` / `status = "disabled"` in both Linux (`.dtso`) and Zephyr (`.overlay`) outputs
  - The Linux IHC interrupt list (`interrupts` and `interrupt-names`) in the `.dtso`
  - The Zephyr IHC channel selection (for example `ihcc_h3_h1`) and the corresponding `zephyr,ipc` entry in the `.overlay`
  - The mailbox/IHC linkage used by the `remoteproc` block in the Linux `.dtso` when AMP is enabled



### Peripherals

The Peripherals table displays all PIC64GX peripherals and allows assigning
each peripheral to **Context A** or **Context B**, selecting which UART is
used for **stdout**, enabling **Inter-Hart Communication (IHC)**, and
inspecting DTSI definitions directly from the UI.


| Peripherals | Context A | Stdout | Context B | Stdout |
|------------|-----------|--------|-----------|--------|
| UART 1 | ☐ | ○ | ☐ | ○ |
| UART 2 | ☐ | ○ | ☐ | ○ |
| ... | | | | |


> **Zephyr compatibility**
>
> When a context is configured to run **Zephyr**, peripherals that are not
> supported by the Zephyr device tree are automatically **greyed out** in the UI.
>
> These peripherals cannot be selected and will never be written into the
> Zephyr `.overlay` file. This prevents generating overlays that would fail
> to compile in Zephyr.
>
> Tooltips explain why a peripheral is unavailable when hovered.

#### DTSI Reference Popup (Hover Feature)
Hovering over any peripheral name displays a popup showing the
corresponding DTSI node definition.

This allows you to:
- Inspect how the peripheral is defined in the device tree
- Verify node names and labels used in overlays
- Understand the mapping without opening DTSI files manually

> The popup can be pinned, dragged, and multiple popups can be open at the same time.


#### AMP Interaction
When **AMP is disabled**:
- Context B is greyed out
- All peripherals belong to **Context A**

When **AMP is enabled**:
- Both Context A and Context B become active
- The UI enforces that no peripheral can belong to both contexts

#### Stdout (UART Console) Selection

For UART peripherals, a **Stdout** option is available per context.
- Each context can select **exactly one UART** as its console
- This selection controls how console output is configured in the generated overlays

> The Configurator automatically generates the correct device tree
> configuration for the selected UART. No manual DTS editing is required.



#### Rules

- A peripheral **cannot** be assigned to both contexts
- When AMP is disabled, all peripherals are automatically assigned to **Context A**
- The UI prevents invalid combinations and enforces mutual exclusion
- The generator writes **every peripheral** into the output overlays with an explicit:

```dts
status = "okay";
status = "disabled";
```


---

## 6. Revert and Refresh actions

### Revert
Clicking the **Revert** button will:

- Prompt the user with a confirm dialog.
- If confirmed:
  - Reloads the **last saved configuration** from the current YAML files.
  - Discards any changes made in the UI

### Refresh

Clicking **Refresh** reloads data from the internal temp YAML files (without confirmation)
Useful to:
- Re-sync changes after manual YAML edits
- Validate consistency between the UI Configurator and YAML files before generation


>Refresh does **not** discard changes, it simply re-reads the current
>working configuration.



---

## 7. Generate Output Files

Clicking **Generate** creates all device tree overlay files and the project
configuration output based on the current UI state.

### Generation Flow

1. You are prompted to select an **output directory**
2. The tool reads the internal YAML configuration
3. The `MANIFEST` file is created or updated if exists, with the output `globalPath` path
4. Output files are generated
5. Temporary working files are cleaned up


### Output Files

| File               | Description |
|--------------------|-------------|
| `global.yaml`      | Complete exported project configuration |
| `context_a.dtso`   | Linux overlay for Context A (if Context A is Linux)|
| `context_b.dtso`   | Linux overlay for Context B (if Context B is Linux)|
| `context_a.dtbo`   | Binary overlays compiled automatically using `dtc` |
| `context_b.dtbo`   | Binary overlays compiled automatically using `dtc`|
| `context_a.overlay`| Zephyr overlay for Context A (if Context A is Zephyr) |
| `context_b.overlay`| Zephyr overlay for Context B (if Context B is Zephyr)|




### What the Generator Produces Automatically

The generator creates fully valid overlays for Linux and Zephyr, including:

- Correct **memory node structure** (main memory vs reserved-memory)
- Automatic **AMP reserved memory blocks** when AMP is enabled
- Correct **CPU status** for all harts
- Correct **IHC / mailbox / remoteproc** configuration
- Correct **stdout configuration** for each context
- Explicit **status = "okay" / "disabled"** for every peripheral
- Zephyr-specific `chosen` entries when Zephyr is selected
- Linux-specific `remoteproc` and mailbox configuration when AMP is enabled
- Proper formatting and structure validated by `dtc`

>No manual editing of the generated files is required.



### Working Files

| File / Folder | Description |
|---------------|-------------|
| `.temp/*.yaml` | Temporary internal working configuration YAML files (auto-deleted)|
| `MANIFEST` | Tracks output path and project metadata (Automatically updates `globalPath` to be able to `Open Project`) |

> The `.temp` folder is removed after generation.



---

## Author

**Santiago Gil – M52397**  
 [santiago.gil@microchip.com](mailto:santiago.gil@microchip.com)

---
