#	This file is part of Shell Script Launcher for Kodi.
#
#	Copyright (C) 2021 wastis    https://github.com/wastis/PulseEqualizerGui
#
#	PulseEqualizerGui is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import os
import sys
import subprocess

import xbmcaddon
import xbmc
import xbmcgui

from log import log
from handle import handle

from menu import MenuGui

addon = xbmcaddon.Addon()
def tr(lid):
	return addon.getLocalizedString(lid)

def parse_flags(flags):
	# takes comma seperated string like "notify,exitcode 0"

	notify = False
	check_exit = False
	expect = 0

	for flag in flags.split(","):
		flag = flag.strip()
		if flag == "notify":
			notify = True
		if flag.startswith("exitcode"):
			expect = int(flag[8:].strip())
			check_exit = True

	return notify, check_exit, expect

def run_addon():
	try:
		cwd = xbmcaddon.Addon().getAddonInfo('path')
		menufile = os.path.expanduser(xbmcaddon.Addon().getSettingString("menufile"))

		log("menufile: " +  menufile)

		try:
			with open(menufile, "r") as f:
				content = f.read().split("\n")
		except FileNotFoundError:
			xbmcgui.Dialog().ok(tr(32100),tr(32101))
			return
		except IsADirectoryError:
			xbmcgui.Dialog().ok(tr(32100),tr(32102))
			return
		except PermissionError:
			xbmcgui.Dialog().ok(tr(32100),tr(32103))
			return
		except Exception as e:
			handle(e)
			xbmcgui.Dialog().ok(tr(32100),tr(32104))
			return

		# parse menu items
		menu_items = []
		for line in content:
			try:
				cols = line.split(":")
				if len(cols) < 3:
					continue

				name = cols[0].strip()
				flags = cols[1].lower()
				exe = ":".join(cols[2:])

				if name == "" or exe == "":
					continue

				menu_items.append((name, exe, flags))

			except:
				continue
		#
		# check if menu file is empty
		#

		if not menu_items:
			xbmcgui.Dialog().ok(tr(32100),tr(32105))
			return

		#
		# check if parameter was given
		#

		if len(sys.argv)>1:
			selected = int(sys.argv[1])
			if selected >= len(menu_items):
				log("no script for %d" % selected)
				return
		else:
			#
			# show menu dialog
			#

			current_skin = xbmc.getSkinDir()

			if os.path.exists(os.path.join(cwd,"resources","skins",current_skin)):
				skin = current_skin
			else:
				skin = "Default"

			ui = MenuGui("menu.xml", cwd, skin, "1080i", menu = menu_items, width = 400)
			ui.doModal()
			selected = ui.selected

		#
		# check if back has been pressed
		#

		if selected < 0:
			log("nothing selected")
			return

		#
		# expand user home ~
		#

		cmd = [\
				os.path.expanduser(item) \
				for item in menu_items[selected][1].split(" ")\
			]

		#
		# parse flags
		#

		notify, check_exit, expect = parse_flags(menu_items[selected][2])

		#
		# execute command
		#

		log("execute: " + " ".join(cmd))

		try:
			exitcode =  int(subprocess.Popen(cmd).wait())

		except Exception as e:
			handle(e)
			xbmcgui.Dialog().ok(tr(32110),tr(32111) % cmd)

		else:
			log("done with exitcode %s " % str(exitcode))

			if check_exit and exitcode != expect:
				xbmcgui.Dialog().ok\
				(\
					tr(32110), \
					tr(32113) %  (menu_items[selected][0], exitcode)\
				)

			elif notify:
				xbmcgui.Dialog().notification\
				(
					tr(32112), \
					menu_items[selected][0],\
					os.path.join(cwd,"resources","media","notify.png")\
				)

	except Exception as e:
		handle(e)
