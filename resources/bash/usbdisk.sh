#!/bin/bash

# Function to list all USB disks
list_usb_disks() {
    lsblk -S -o NAME,TRAN,VENDOR,MODEL | awk '$2 == "usb" { print $1 }' | while read -r dev; do
        SIZE=$(lsblk -dno SIZE "/dev/$dev")
        MODEL=$(lsblk -dno MODEL "/dev/$dev")
        echo "$dev - $SIZE - $MODEL"
    done
}

# Function to disconnect a given USB disk
disconnect_usb_disk() {
    INPUT_LINE="$1"
    DEV=$(echo "$INPUT_LINE" | awk '{print $1}')
    DEVICE="/dev/$DEV"

    # Confirm it's a USB disk
    if ! lsblk -S -o NAME,TRAN | awk '$2 == "usb" { print $1 }' | grep -Fxq "$DEV"; then
        echo "Error: $DEVICE is not a USB disk."
        exit 1
    fi

    # Find all mounted partitions of this device
    MOUNTED_PARTS=$(lsblk -ln -o NAME,MOUNTPOINT "$DEVICE" | awk '$2 != "" { print $1 }')

    # Unmount each partition
    for PART in $MOUNTED_PARTS; do
        echo "Unmounting /dev/$PART..."
        udisksctl unmount -b "/dev/$PART" || {
            echo "Failed to unmount /dev/$PART"
            exit 1
        }
    done

    # Double-check nothing is still mounted
    STILL_MOUNTED=$(lsblk -no MOUNTPOINT "$DEVICE" | grep -v '^$')
    if [ -n "$STILL_MOUNTED" ]; then
        echo "Device is still mounted. Cannot power off."
        exit 1
    fi

    # Power off
    echo "Powering off $DEVICE..."
    udisksctl power-off -b "$DEVICE"
}

# Main logic
if [ -z "$1" ]; then
    list_usb_disks
    exit 0
else
    disconnect_usb_disk "$1"
fi

