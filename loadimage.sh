#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

AXF_FILE=$1
BIN_FILE=$2
GDB_FILE=$SCRIPT_DIR/d.gdb
CMD_STR="arm-none-eabi-gdb $AXF_FILE -x $GDB_FILE"

JLINK_FILE=$SCRIPT_DIR/temp.jlink
echo "
r
h
loadfile $BIN_FILE 0x60800000
r
exit" > $JLINK_FILE


source $SCRIPT_DIR/sense_jlink.sh $SCRIPT_DIR/temp.jlink

# tmux new-session -d $CMD_STR
# source $SCRIPT_DIR/tmux_console.sh