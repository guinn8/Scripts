#!/bin/bash

SCRIPT_DIR=~/Scripts

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

echo $JLINK_FILE

source $SCRIPT_DIR/sense_jlink.sh 
rm $JLINKFILE

tmux new-session -d $CMD_STR
source $SCRIPT_DIR/tmux_console.sh