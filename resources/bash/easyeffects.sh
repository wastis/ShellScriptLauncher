#!/bin/bash

# Function to get output profiles
get_output_profiles() {
    LANG=C easyeffects -p | grep "^Output Presets:" | cut -d':' -f2 | tr ',' '\n' | sed '/^\s*$/d' | sed 's/^[ \t]*//;s/[ \t]*$//'
}

# No arguments: list available profiles
if [ -z "$1" ]; then
    get_output_profiles
    exit 0
fi

# One argument: try to switch to the given profile
PROFILE_NAME="$1"

if get_output_profiles | grep -Fxq "$PROFILE_NAME"; then
    easyeffects -l "$PROFILE_NAME"
else
    echo "Error: Profile '$PROFILE_NAME' not found."
    exit 1
fi
