#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJ_BASE=`realpath $SCRIPT_DIR/../..` # !! NEEDS MODIFICATION IF MOVED !!
export BOOTLOADER_BASE=$PROJ_BASE/bootloader
export CROSS_COMPILE=arm-none-eabi-
export TARGET=proto-d # needed to load the flash over usb
export BUILD_FLAG=debug

tmux new-session -d 'make -C $BOOTLOADER_BASE -j && sleep 1 &&
                        arm-none-eabi-gdb $BOOTLOADER_BASE/build/proto-d/bin/bootloader.axf -x $PROJ_BASE/scripts/gdb/d.gdb -q'

source $SCRIPT_DIR/tmux_console.sh
