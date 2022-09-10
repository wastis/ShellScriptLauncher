#	This file is part of  Shell Script Launcher for Kodi.
#
#	Copyright (C) 2022 wastis    https://github.com/wastis/BluetoothManager
#
#	Bluetooth Manager is free software; you can redistribute it and/or modify
#	it under the terms of the GNU Lesser General Public License as published
#	by the Free Software Foundation; either version 3 of the License,
#	or (at your option) any later version.
#
#

import xbmcgui
import xbmcaddon
from xbmcgui import ListItem

from log import log
from handle import handle
from handle import opthandle

addon = xbmcaddon.Addon()
def tr(lid):
	return addon.getLocalizedString(lid)

class MenuGui(  xbmcgui.WindowXMLDialog  ):
	def __init__( self, *_args, **kwargs ):
		self.cwd = _args[1]
		self.icon_path = self.cwd + "resources/skins/Default/media/"
		self.menu = kwargs["menu"]

	def onInit( self ):
		self.item_list = self.getControl(2000)
		self.item_list_bk = self.getControl(2001)

		item_height = 80
		item_cnt = len(self.menu)

		max_height = self.item_list.getHeight()
		width = self.item_list.getWidth()

		window_height = item_height * item_cnt
		if window_height > max_height:
			window_height = max_height

		y = int((1080 - window_height) / 2)

		log(str(y))

		self.item_list.setHeight(window_height)
		self.item_list_bk.setHeight(window_height)

		x = int((1920 - width)/2)

		self.item_list.setWidth(width)
		self.item_list_bk.setWidth(width)

		self.item_list.setPosition(x,y)
		self.item_list_bk.setPosition(x,y)

		for menuitem in self.menu:
			item = ListItem(menuitem[0], "")
			self.item_list.addItem(item)

		self.setFocusId(2000)

	#
	# dialog action handling
	#

	def end_gui(self):
		log("end_gui")
		self.selected = -1
		self.close()

	def ok_pressed(self):
		self.selected = self.item_list.getSelectedPosition()
		self.close()

	def onAction( self, action ):
		#log("action id %s" % action.getId())

		#OK pressed
		if action.getId() in [7, 100]:
			self.ok_pressed()

		#Cancel
		if action.getId() in [92,10,18]:
			self.end_gui()
