#!/bin/bash

# Dummy script for scriptmenu testing
# - If no argument is given, it prints 5 menu items
# - If an argument is given, it prints the argument and exits with 0

if [ -z "$1" ]; then
    echo "Item 1"
    echo "Item 2"
    echo "Item 3"
    echo "Item 4"
    echo "Item 5"
else
    echo "You passed: $1"
    exit 0
fi
