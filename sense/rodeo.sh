#!/bin/bash

CROSS_COMPILE=arm-none-eabi- TARGET=evk make ll_ex -j

# Exit if compilation fails
if [ $? == 0 ]; then
    printf "\nCompilation success!\n\n"
else
    printf "\nCompilation fail, exiting...\n\n"
    exit 1
fi

source ~/Scripts/jlink_load.sh build/evk/bin/ll.axf 0x60800000
source ~/Scripts/gdb_connect.sh build/evk/bin/ll.axf