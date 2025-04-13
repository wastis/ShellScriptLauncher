#	This file is part of  Shell Script Launcher for Kodi.
#
#	Copyright (C) 2025 wastis https://github.com/wastis/ShellScriptLauncher
#
#	Shell Script Launcher is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

def parse_menu_file(filepath):
    """
    Parses a ':' separated text file defining a menu structure.

    Args:
        filepath (str): The path to the menu definition file.

    Returns:
        list: A list of dictionaries representing the top-level menu items.
              Each dictionary can represent a menu entry or a submenu.
              Submenus contain a 'sub_items' key holding a list of their items.
              Returns an empty list if the file is empty or only contains
              comments/blank lines.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If structural errors, flag errors, or parsing errors
                    are found in the file (includes line number).

    Data Structure of Returned Items:
        - Regular Item:
          {
              'display': str,
              'command': str,
              'flags': {
                  'notify': bool,
                  'show': bool,
                  'exitcode': int | None # Integer if specified, else None
              },
              'line': int # Original line number
          }
        - Submenu Item:
          {
              'display': str,
              'command': str, # Often empty/irrelevant for submenu container
              'flags': {
                  'is_submenu': True
              },
              'sub_items': list, # Contains items (regular or submenu)
              'line': int # Original line number
          }
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at '{filepath}'")

    # The main structure is a list for the top level items
    main_menu = []
    # Stack to keep track of the current list of items being added to
    # Starts with the main_menu list
    stack = [main_menu]
    # Keep track of submenu start lines for error reporting
    submenu_start_lines = []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments (lines starting with #)
        if not line or line.startswith('#'):
            continue

        parts = line.split(':', 2)
        if len(parts) != 3:
            raise ValueError(
                f"Error on line {line_num}: Line does not contain exactly"
                f" three ':' separated columns. Content: '{line}'"
            )

        display_text, flags_str, command = [part.strip() for part in parts]

        if not display_text:
             raise ValueError(
                f"Error on line {line_num}: display_text cannot be empty."
                f" Content: '{line}'"
            )

        # --- Parse Flags ---
        raw_flags = [flag.strip() for flag in flags_str.split(',') if flag.strip()]
        parsed_flags = {
            'notify': False,
            'show': False,
            'exitcode': None,
            'is_submenu': False,
            'is_subend': False,
            'is_scriptmenu': False,
        }
        exitcode_value = None # Keep track if exitcode was processed in this line

        # Check for modal flags first
        if 'submenu' in raw_flags:
            if len(raw_flags) > 1:
                raise ValueError(
                    f"Error on line {line_num}: 'submenu' flag cannot be combined"
                    f" with other flags. Found: {raw_flags}"
                )
            parsed_flags['is_submenu'] = True
        elif 'subend' in raw_flags:
            if len(raw_flags) > 1:
                raise ValueError(
                    f"Error on line {line_num}: 'subend' flag cannot be combined"
                    f" with other flags. Found: {raw_flags}"
                )
            parsed_flags['is_subend'] = True
        else:
            # Process non-modal flags
            for flag in raw_flags:
                if flag == 'notify':
                    parsed_flags['notify'] = True
                elif flag == 'show':
                    parsed_flags['show'] = True
                elif flag == 'scriptmenu':
                    parsed_flags['is_scriptmenu'] = True
                # --- Updated exitcode parsing without re ---
                elif flag.startswith('exitcode'):
                    # Use split(None, 1) to handle potential multiple spaces
                    # after 'exitcode' and split only once.
                    flag_parts = flag.split(None, 1)

                    # Check if split produced two parts ('exitcode', 'value')
                    # and the first part is exactly 'exitcode'
                    if len(flag_parts) == 2 and flag_parts[0] == 'exitcode':
                        value_part = flag_parts[1]
                        # Check if the value part consists ONLY of digits
                        if value_part.isdigit():
                            if parsed_flags['exitcode'] is not None:
                                raise ValueError(
                                    f"Error on line {line_num}: Multiple 'exitcode'"
                                    f" flags specified. Found: {raw_flags}"
                                )
                            # Convert to integer (no try-except needed due to isdigit)
                            exitcode_value = int(value_part)
                            parsed_flags['exitcode'] = exitcode_value
                        else:
                            # The part after 'exitcode ' was not a valid integer
                            raise ValueError(
                                f"Error on line {line_num}: Invalid 'exitcode'"
                                f" value in flag '{flag}'. Value must be an integer."
                            )
                    else:
                        # Covers cases like "exitcode" alone, "exitcodeXYZ",
                        # "exitcode multiple words" etc.
                        raise ValueError(
                            f"Error on line {line_num}: Invalid 'exitcode' flag"
                            f" format. Use 'exitcode N' where N is an integer."
                            f" Found: '{flag}'"
                        )
                # --- End of updated exitcode parsing ---
                else:
                    raise ValueError(
                        f"Error on line {line_num}: Unknown flag '{flag}'."
                        f" Allowed flags: submenu, subend, notify, show,"
                        f" exitcode N."
                    )

        # --- Process based on Flags and Update Structure ---
        current_level_list = stack[-1]

        if parsed_flags['is_submenu']:
            # Start a new submenu
            submenu_item = {
                'display': display_text,
                'command': command, # Command might be ignored for submenu container
                'flags': {'is_submenu': True},
                'sub_items': [], # The list for items within this submenu
                 'line': line_num
            }
            current_level_list.append(submenu_item)
            # Push the new sub_items list onto the stack for the next items
            stack.append(submenu_item['sub_items'])
            submenu_start_lines.append(line_num) # Track entry point

        elif parsed_flags['is_subend']:
            # End the current submenu
            if len(stack) <= 1:
                raise ValueError(
                    f"Error on line {line_num}: 'subend' found without a matching"
                    f" 'submenu'. Cannot end the top-level menu."
                )
            stack.pop() # Go back up one level
            submenu_start_lines.pop() # Forget last submenu start line
            # The display_text and command for 'subend' are usually ignored

        else:
            # Regular menu item
            if not stack: # Should theoretically not happen with start stack [main_menu]
                 raise ValueError(
                     f"Internal Error on line {line_num}: Stack is empty,"
                     f" cannot add item '{display_text}'."
                 )

            menu_item = {
                'display': display_text,
                'command': command,
                'flags': {
                    'notify': parsed_flags['notify'],
                    'show': parsed_flags['show'],
                    'exitcode': parsed_flags['exitcode'],
                    'scriptmenu': parsed_flags['is_scriptmenu'],
                },
                'line': line_num
            }
            current_level_list.append(menu_item)

    # --- Final Validation ---
    if len(stack) > 1:
        last_submenu_line = submenu_start_lines[-1]
        raise ValueError(
            f"Error: End of file reached, but submenu started on line"
            f" {last_submenu_line} was not closed with 'subend'."
        )

    return main_menu
