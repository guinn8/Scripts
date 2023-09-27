#!/bin/bash

CROSS_COMPILE=arm-none-eabi- TARGET=proto-d BUILD_FLAG=dev make gw-app-sign -j

# Exit if compilation fails
if [ $? == 0 ]; then
    printf "\nCompilation success!\n\n"
else
    printf "\nCompilation fail, exiting...\n\n"
    exit 1
fi

source ~/Scripts/jlink_load.sh build/proto-d/bin/sense-gw-signed.bin 0x60800000
source ~/Scripts/gdb_connect.sh build/proto-d/bin/sense-gw.axf
