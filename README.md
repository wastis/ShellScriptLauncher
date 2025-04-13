# Kodi Shell Script Launcher

## Kodi Addon: Shell Script Executor

This Kodi addon allows users to execute shell scripts or commands directly from the Kodi interface.

**Key Features:**

* **Menu-Driven Execution:** Presents a user-friendly menu to select the desired script for execution.
* **Configurable Menu:** The menu is defined in a simple text file.
* **Colon-Separated Format:** The menu file uses a colon (`:`) to separate menu items (see `example.menu`).
* **Menu File Selection:** Users can specify the path to their menu file within the addon settings.

**Example Scripts:**

The addon includes the following example scripts:

* Select wlan ssid (wlan needs to be present, script does not ask for keys)
* Select easyeffects preset (easyeffects need to be present, presets need to be defined)
* usb-disk disconnect

[Version 2.0.0](https://github.com/wastis/LinuxAddonRepo)

<img src="resources/media/icon.png" alt="drawing" width="200"/> 



## Menu File Format: Quick Start Guide

This is a quick overview of the menu file format. For full details, see below in the main documentation.

1.  **Purpose:** Create a text file to define menu items for the Shell Script Launcher addon.
2.  **Format:** Each line defines one item using **three** parts separated by colons (`:`):
    ```
    Display Name : Flags : Command
    ```
    * `Display Name`: Text shown in the Kodi menu. **Required**.
    * `Flags`: Keywords (comma-separated) to control behavior. **Optional**.
    * `Command`: Shell command/script to run. **Optional**.
3.  **Common Flags:**
    * (No Flags): Just runs the command silently.
    * `notify`: Shows a Kodi notification popup when the command finishes.
    * `show`: Shows the command's text output in a Kodi window when finished.
    * `exitcode 0`: Checks if the command finished successfully (exit code 0). Shows an error if not.
    * `submenu` / `subend`: Creates a subfolder structure. `submenu` starts a folder, `subend` ends it. These flags **must** be used alone on their line.
    * `scriptmenu`: (Advanced) Runs a command whose output dynamically creates a temporary submenu.
4.  **Comments:** Lines starting with `#` are ignored.
5.  **Save:** Save the file (e.g., `mymenu.txt`) and configure it in the addon settings.

---

## Very Simple Example (`simple_menu.txt`)

```plaintext
# --- My Simple Menu ---

# Command with no flags
List Home Folder::ls -l ~

# Command with notification on completion
Backup Something Important:notify:/path/to/my_backup_script.sh

# Command that checks for successful execution
Check Internet:exitcode 0:ping -c 1 8.8.8.8

# A simple sub-menu (like a folder)
Utility Scripts:submenu:
  Clean Cache::/scripts/clean_cache.sh
  Check Updates:notify:/scripts/check_updates.sh
Utility Scripts:subend:
```
---
# Menu Definition File Format

This document describes the format for the menu definition file. This file defines the menu items users can select, associated commands to execute, and flags that control execution behavior (like success checks and notifications). It's a **colon-delimited** text file, typically assigned within the addon's settings.

## 1. General Format

* **Plain Text:** The file **must** be a plain text file (e.g., UTF-8 encoding is recommended).
* **Line-Based:** Each non-empty, non-comment line defines either a menu item or a structure directive (`submenu` / `subend`).
* **Columns:** Each meaningful line **must** consist of exactly three parts, separated by a colon (`:`).
    ```
    display_text:flags:command
    ```
* **Whitespace:** Whitespace (spaces, tabs) immediately around the colons (`:`) or commas (`,`) within the flags section is generally ignored during parsing. Leading/trailing whitespace on each line is also ignored.

## 2. Columns Explained

1.  **`display_text` (**Required**)**
    * This is the text that will be displayed to the user in the menu for this item or submenu title (e.g., `Backup addon data`).
    * It **cannot** be empty.

2.  **`flags` (**Optional**)**
    * This section contains a **comma-separated** list of keywords (flags) that modify the behavior or structure of the menu item.
    * If this section is empty, the line represents a standard menu item that simply runs its command.
    * See the **Flags** section below for details on available flags and rules.
    * Example: `notify,exitcode 0` or `submenu` or `scriptmenu,notify`

3.  **`command` (**Optional**)**
    * This is the shell command or script (including any arguments) to be executed when the user selects this menu item (e.g., `/bin/tar -czf ~/kodi_userdata.tgz ~/.kodi/userdata`).
    * It can be empty, especially for `submenu` or `subend` lines where it's often ignored.
    * If the command or its arguments contain spaces, they should generally be handled correctly as part of this single field.

## 3. Flags

Flags control how the menu item behaves or define the menu structure. Flags are comma-separated.

**Structural Flags (Mutually Exclusive):**

These flags define the static menu hierarchy. **Only one** of these can be used on a line, and **no other flags** (like `notify`, `show`, `exitcode`, `scriptmenu`) can be present on the same line.

* `submenu`
    * Indicates the start of a new, statically defined submenu level.
    * The `display_text` of this line becomes the title or selectable item that opens this submenu.
    * The `command` on this line is typically ignored.
    * All subsequent items belong to this submenu until a corresponding `subend` is encountered.

* `subend`
    * Indicates the end of the *most recently opened* static submenu.
    * Processing returns to the previous menu level.
    * Every `submenu` **must** have a corresponding `subend`.
    * The `display_text` and `command` on this line are typically ignored.

**Behavioral Flags (Combinable):**

These flags modify how a regular menu item (one that is *not* `submenu` or `subend`) behaves. They can generally be combined with each other (unless noted otherwise).

* `scriptmenu`
    * This powerful flag indicates that the `command` is expected to generate a list of dynamic submenu items.
    * **Workflow:**
        1. The `command` is executed once. It **must** exit successfully (typically exit code 0) for the process to continue.
        2. The standard output (`stdout`) of the command is read. Each non-empty line of the output becomes a display item in a dynamically generated submenu.
        3. If the output is empty, a notification is shown, and no submenu appears.
        4. If output is present, the dynamic submenu is shown to the user.
        5. If the user selects an item from this dynamic menu, the original `command` is executed *a second time*, with the text of the selected item appended as the final argument.
        6. Other behavioral flags (`notify`, `show`, `exitcode N`) present on the *original* `scriptmenu` line are applied based on the result of this **second** command execution.
    * Useful for menus whose content depends on the current system state (e.g., listing available networks, drives, or configuration profiles).
    * Can be combined with `notify`, `show`, `exitcode N`.

* `notify`
    * If present, the application typically **displays a notification window** when the associated command execution has finished.
    * For `scriptmenu` items, this applies after the *second* execution (if an item was selected from the dynamic menu).

* `show`
    * If present, the standard output (`stdout` and `stderr`) of the `command` execution is displayed in a Kodi dialog window after the command finishes.
    * For `scriptmenu` items, this applies to the output of the *second* execution.
    * *(Note: Some older examples or comments might refer to this as `print`, but the correct flag recognized by the script is `show`)*.

* `exitcode N`
    * Specifies the expected successful exit code (return status) from the executed `command`.
    * `N` **must** be a non-negative integer (e.g., `0`, `1`, `127`). There **must** be a space between `exitcode` and the number.
    * This flag **checks if the return value** of the script equals `N`. If the script's actual exit code **does not** match `N`, the application typically **displays a message box** indicating the mismatch or failure. `exitcode 0` is commonly used to check for successful execution.
    * Only one `exitcode N` flag can be present on a single line.
    * For `scriptmenu` items, this check applies to the exit code of the *second* execution.
    * *(Note: Sometimes referred to as "legacy" but still functional for defining expected success).*

**Flag Rules Summary:**

* A line can have:
    * `submenu` (and nothing else)
    * **OR** `subend` (and nothing else)
    * **OR** a combination of behavioral flags (`notify`, `show`, `exitcode N`, `scriptmenu`).
* `submenu` and `subend` **cannot** be combined with *any* other flags on the same line.
* `notify`, `show`, `exitcode N`, and `scriptmenu` can generally be used together (e.g., `scriptmenu,notify,exitcode 0`).

## 4. Hierarchy (Submenus)

* **Static Submenus:** Defined by `submenu` and `subend` flags. Items physically between these lines in the file belong to that submenu. Can be nested.
* **Dynamic Submenus:** Generated by commands marked with the `scriptmenu` flag based on their output at runtime.
* The main (top-level) menu consists of items not enclosed within any `submenu`/`subend` block.

## 5. Comments and Blank Lines

* Lines starting with a hash symbol (`#`) are treated as comments and are ignored.
* Blank lines (lines containing only whitespace) are also ignored.

## 6. Example File (`example.menu`)

This example demonstrates static submenus, basic commands, and the dynamic `scriptmenu` flag.

```plaintext
# Static Submenu: Ping options
< ping a server >:submenu:
    Ping Server 1:exitcode 0:ping -c 1 192.168.1.1
    Ping 8.8.8.8:notify, exitcode 0:ping -c 1 8.8.8.8
< ping a server >:subend:

# Static Submenu: Wake-on-LAN options
- wake a server -:submenu:
    wake server video::/usr/bin/wakeonlan 94:de:80:a1:c3:5c
    wake server data::/usr/bin/wakeonlan 8C:89:A5:57:88:FC
- wake a server -:subend:

<< Dynamic Menus >>:submenu:

	# Scriptmenu Example: Simple script demonstrating dynamic item generation
	# The dummy.sh script just prints a few static lines to stdout.
	# 'show' flag will display output of the *second* run (after selection).
	< dummy >:scriptmenu,show:~/.kodi/addons/script.shellscript.launcher/resources/bash/dummy.sh

	# Static Submenu: Misc tools containing more dynamic menus
	< maybe usefull >:submenu:
		# Dynamic menu: List Easyeffects presets
		# easyeffects.sh lists presets; selecting one applies it (second run).
		switch easyeffects profile:scriptmenu:~/.kodi/addons/script.shellscript.launcher/resources/bash/easyeffects.sh

		# Dynamic menu: List USB drives to disconnect
		# usbdisk.sh lists mount points; selecting one attempts unmount (second run).
		unmount usb disk:scriptmenu:~/.kodi/addons/script.shellscript.launcher/resources/bash/usbdisk.sh
		
		# Scriptmenu Example: List WLANs dynamically
		# wlan.sh outputs available network names. Selecting one might try to connect.
		# notify flag shows notification after connection attempt (second run).
		# exitcode 0 checks if connection attempt (second run) was successful.
		wlan networks (please be patient):scriptmenu,notify,exitcode 0:~/.kodi/addons/script.shellscript.launcher/resources/bash/wlan.sh
		
	< maybe usefull >:subend:
<< Dynamic Menus >>:subend:

# Standard Command Examples: Run backup commands
# - notify flag shows a message when done
Backup addon data:notify:/bin/tar -czf ~/kodi_addon_data.tgz ~/.kodi/userdata/addon_data

# Silent backup (no flags)
Backup keymaps::/bin/tar -czf ~/kodi_keymaps.tgz ~/.kodi/userdata/keymaps
Backup userdata::/bin/tar -czf ~/kodi_userdata.tgz ~/.kodi/userdata
```
