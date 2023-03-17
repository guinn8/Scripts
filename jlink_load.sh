#!/bin/bash

# Copyright (c) 2022 Simply Embedded Inc.
# All Rights Reserved.
#
# File: jlink_load.sh
# Brief: loads a binary onto the device via JLink
# args:
#   BIN_FILE: binary file to load
#   OFFSET: location in memory to load file (ex. 0x608000000)

BIN_FILE=$1
OFFSET=$2
JLINK_SCRIPT=~/Scripts/temp.jlink

# we need to use a temporary file to pass a command string to JLink
rm $JLINK_SCRIPT
echo "
r
h
loadfile $BIN_FILE $OFFSET
r
exit" > $JLINK_SCRIPT

source ~/Scripts/jlink_connect.sh $JLINK_SCRIPT
rm $JLINK_SCRIPT
