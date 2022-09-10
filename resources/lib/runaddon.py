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
import subprocess

import xbmcaddon
import xbmc

from log import log
from handle import handle

from menu import MenuGui

def run_addon():
	try:
		cwd = xbmcaddon.Addon().getAddonInfo('path')
		menufile = os.path.expanduser(xbmcaddon.Addon().getSettingString("menufile"))

		log("menufile: " +  menufile)

		with open(menufile, "r") as f:
			content = f.read().split("\n")

		menu_items = []
		for line in content:
			try:
				pos = line.find(":")
				if pos <0 : continue
				expos = line.find(":",pos + 1)

				name =  line[:pos].strip()
				block = line[pos + 1:expos].strip() == "blocking"
				exe = line[expos + 1:].strip()

				if name == "":
					continue
				if exe == "":
					continue
				menu_items.append((name, block, exe))

			except:
				continue

		if not menu_items:
			log("no menu entries found in menu file")
			return

		current_skin = xbmc.getSkinDir()
		log(current_skin)

		if os.path.exists(os.path.join(cwd,"resources","skins",current_skin)):
			skin = current_skin
		else:
			skin = "Default"

		ui = MenuGui("menu.xml", cwd, skin, "1080i", menu = menu_items, width = 400)
		ui.doModal()
		selected = ui.selected
		if selected < 0:
			log("nothing selected")
			return

		cmd = [os.path.expanduser(item) for item in menu_items[selected][2].split(" ")]
		block =  menu_items[selected][1]
		log("run: " + str(block) + " "+ " ".join(cmd))

		if block:
			os.system(" ".join(cmd))
		else:
			subprocess.Popen(cmd)
		log("done")

	except Exception as e:
		handle(e)
