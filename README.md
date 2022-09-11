# Kodi Shell Script Launcher

Kodi addon to execute shell scripts or commands. It displays a menu to select the script that shall be executed. The menu is defined in a text file, that is ":" separated (see example.menu). The menu file can be selected in the addon settings.

[Version 1.0.0](https://github.com/wastis/LinuxAddonRepo)

<img src="resources/media/icon.png" alt="drawing" width="200"/> 

## Menu file

The menu file defines the menu items, script success flags and the command. It is a colon delimited table file, that can be assigned in the addon settings.

	Name 1:flags:command 1
	Name 2:flags:command 1
	....	

The flags are comma separated. Currently there are two flags defined

- notify	 (*displays a notification window, when the script has ended*)
- exitcode value (*checks if the return value of the script equals value. Displays a message box if it does not match.*)

### example.menu
	Backup addon data:notify:/bin/tar -czf ~/kodi_addon_data.tgz ~/.kodi/userdata/addon_data
	Backup keymaps::/bin/tar -czf ~/kodi_keymaps.tgz ~/.kodi/userdata/keymaps
	Backup userdata	::/bin/tar -czf ~/kodi_userdata.tgz ~/.kodi/userdata
	Ping Server:notify,exitcode 0:ping -c 1 192.168.1.1


2022 wastis


