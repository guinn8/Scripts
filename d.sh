#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJ_BASE=`realpath $SCRIPT_DIR/../..` # !! NEEDS MODIFICATION IF MOVED !!
export CROSS_COMPILE=arm-none-eabi-
export TARGET=proto-d
export BUILD_FLAG=debug

time make -C $PROJ_BASE id-app-sign -j
source scripts/release_prep/trunc_binary.sh
time source $PROJ_BASE/scripts/gdb/sense_jlink.sh /home/guinn8/Code/human-id/scripts/gdb/sense_id_signed.jlink

echo "Press any key to continue..."
read -n 1

tmux new-session -d 'arm-none-eabi-gdb $PROJ_BASE/build/proto-d/bin/sense-id.axf -x $PROJ_BASE/scripts/gdb/d.gdb -q'

source $SCRIPT_DIR/tmux_console.sh