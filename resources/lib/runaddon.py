#	This file is part of  Shell Script Launcher for Kodi.
#
#	Copyright (C) 2022 / 2025 wastis https://github.com/wastis/ShellScriptLauncher
#
#	Shell Script Launcher is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import os
import sys
from subprocess import Popen, PIPE

import xbmcaddon
import xbmc
import xbmcgui

from log import log
from handle import handle

from menu import MenuGui
from mparser import parse_menu_file

addon = xbmcaddon.Addon()

def tr(lid):
	"""Retrieve the localized string for the given id."""
	return addon.getLocalizedString(lid)

def get_skin(cwd):
	"""Return the current skin if available; otherwise, default to 'Default'."""
	current_skin = xbmc.getSkinDir()
	skin_path = os.path.join(cwd, "resources", "skins", current_skin)
	return current_skin if os.path.exists(skin_path) else "Default"

def execute_command(cmd, flags, cwd, skin):
	"""
	Executes the command with given flags.
	Returns a tuple (exitcode, stdout_text, combined_output)
	or (None, None, None) in case of an exception.
	"""
	log("execute: " + " ".join(cmd))
	try:
		process = Popen(cmd, stdout=PIPE, stderr=PIPE)
		out, err = process.communicate()
		exitcode = process.returncode

		stdout_text = out.decode("utf-8", errors="replace").strip()
		stderr_text = err.decode("utf-8", errors="replace").strip()
		combined_output = "\n".join(filter(None, [stdout_text, stderr_text])) or "(no output)"
	except Exception as e:
		handle(e)
		xbmcgui.Dialog().ok(tr(32110), tr(32111) % " ".join(cmd))
		return None, None, None

	log("done with exitcode %s" % str(exitcode))
	return exitcode, stdout_text, combined_output

def process_scriptmenu(cmd, stdout_text, cwd, skin, flags, item):
	"""
	When a scriptmenu is called and finishes successfully, this function:
	  - Splits its stdout into individual submenu items.
	  - Displays the submenu to the user.
	  - If a submenu item is selected, it calls the script again with the selected item appended as a parameter.
	"""
	# Build submenu items from each non-empty line in stdout
	lines = [line.strip() for line in stdout_text.splitlines() if line.strip()]
	if not lines:
		xbmcgui.Dialog().notification(
			"Script",
			tr(32114),
			os.path.join(cwd, "resources", "media", "notify.png")
		)
		return

	submenu_items = [{'display': line} for line in lines]

	# Present submenu dialog using MenuGui
	ui = MenuGui("menu.xml", cwd, skin, "1080i", menu=submenu_items, width=400)
	ui.doModal()
	selected = ui.selected

	if selected < 0:
		# User cancelled submenu selection
		return

	selected_line = submenu_items[selected]['display']
	# Append the selected parameter to the original command
	new_cmd = cmd + [selected_line]
	log("execute (scriptmenu with parameter): " + " ".join(new_cmd))
	exitcode, stdout_text2, combined_output2 = execute_command(new_cmd, {}, cwd, skin)

	if exitcode is None:
		return

	# exit code not matching
	elif flags.get('exitcode', None)  is not None and exitcode != flags.get('exitcode', 0):
		xbmcgui.Dialog().ok(tr(32110), tr(32113) % (item, exitcode))

	elif flags.get('show', False):
		xbmcgui.Dialog().ok(tr(32112), combined_output2)

	elif flags.get('notify', False):
		xbmcgui.Dialog().notification(
			tr(32112),
			stdout_text2,
			os.path.join(cwd, "resources", "media", "notify.png")
		)

def navigate(menu_stack, cwd, skin):
	"""
	Recursive function to show and navigate through the menu.
	"""
	current_items = menu_stack[-1]
	ui = MenuGui("menu.xml", cwd, skin, "1080i", menu=current_items, width=400)
	ui.doModal()
	selected = ui.selected

	if selected < 0:
		if len(menu_stack) > 1:
			# Go one level up in the menu tree
			menu_stack.pop()
			return navigate(menu_stack, cwd, skin)
		else:
			# Exit at the root level
			log("nothing selected at root level")
			return

	item = current_items[selected]

	# If the item contains sub-items, dive into the submenu
	if 'sub_items' in item:
		menu_stack.append(item['sub_items'])
		return navigate(menu_stack, cwd, skin)

	# Build command from the item command string
	cmd = [os.path.expanduser(part) for part in item['command'].split() if part]
	flags = item.get('flags', {})

	exitcode, stdout_text, combined_output = execute_command(cmd, flags, cwd, skin)
	if exitcode is None:
		return

	# Process based on flags
	if flags.get('scriptmenu', False):
		if exitcode != 0:
			xbmcgui.Dialog().ok(tr(32110), combined_output)
		else:
			process_scriptmenu(cmd, stdout_text, cwd, skin, flags, item['display'])

	# exit code not matching
	elif flags.get('exitcode', None)  is not None and exitcode != flags.get('exitcode', 0):
		xbmcgui.Dialog().ok(tr(32110), tr(32113) % (item['display'], exitcode))

	elif flags.get('show', False):
		xbmcgui.Dialog().ok(tr(32112), combined_output)

	elif flags.get('notify', False):
		xbmcgui.Dialog().notification(
			tr(32112),
			item['display'],
			os.path.join(cwd, "resources", "media", "notify.png")
		)

def run_addon():
	"""
	Main function for running the addon.
	It sets up the environment, reads the menu file, and initiates the menu navigation.
	"""
	try:
		cwd = xbmcaddon.Addon().getAddonInfo('path')
		menufile = os.path.expanduser(xbmcaddon.Addon().getSettingString("menufile"))
		log("menufile: " + menufile)

		try:
			menu_items = parse_menu_file(menufile)
		except FileNotFoundError:
			xbmcgui.Dialog().ok(tr(32100), tr(32101))
			return
		except IsADirectoryError:
			xbmcgui.Dialog().ok(tr(32100), tr(32102))
			return
		except PermissionError:
			xbmcgui.Dialog().ok(tr(32100), tr(32103))
			return
		except ValueError as e:
			xbmcgui.Dialog().ok(tr(32100), str(e))
			return
		except Exception as e:
			handle(e)
			xbmcgui.Dialog().ok(tr(32100), tr(32104))
			return

		if not menu_items:
			xbmcgui.Dialog().ok(tr(32100), tr(32105))
			return

		skin = get_skin(cwd)
		# Begin navigation at the root menu level
		navigate([menu_items], cwd, skin)

	except Exception as e:
		handle(e)
