#!/bin/bash

if [ $# -eq 0 ]; then
    # Get currently connected SSID
    connected_ssid=$(nmcli -t -f IN-USE,SSID dev wifi list | awk -F: '$1 == "*" {print $2; exit}')
    
    # List unique SSIDs with connection indicator
    nmcli -t -f SSID dev wifi list | sort -u | while read -r ssid; do
        if [ -n "$ssid" ]; then  # Skip empty lines
            if [ "$ssid" = "$connected_ssid" ]; then
                echo "* $ssid"
            else
                echo "  $ssid"
            fi
        fi
    done

elif [ $# -eq 1 ]; then
	ssid="${1#"${1%%[![:space:]]*}"}"  # Trim leading whitespace
    ssid="${ssid%"${ssid##*[![:space:]]}"}"  # Trim trailing whitespace

    echo "Connecting to: $ssid"
    nmcli dev wifi connect "$ssid"

else
    echo "Usage: $0 [SSID]" >&2
    echo "  Run without arguments to list networks" >&2
    echo "  Provide SSID to connect" >&2
    exit 1
fi
