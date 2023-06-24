#!/bin/bash

# Copyright (c) 2023 Simply Embedded Inc.
# All Rights Reserved.
#
# File: jlink_load.sh
# Brief: loads a binary onto the device via JLink
# args:
#   BIN_FILE: binary file to load
#   OFFSET: location in memory to load file (ex. 0x608000000)
#   DEV_ID (optional): device id (default MIMXRT1021XXX5A)

BIN_FILE=$1
OFFSET=$2
DEV_ID=${3:-MIMXRT1021XXX5A}  # default to MIMXRT1021XXX5A if not provided
JLINK_SCRIPT=~/Scripts/temp.jlink

# we need to use a temporary file to pass a command string to JLink
rm $JLINK_SCRIPT
echo "
r
h
loadfile $BIN_FILE $OFFSET
r
exit" > $JLINK_SCRIPT

source ~/Scripts/jlink_connect.sh $JLINK_SCRIPT $DEV_ID
rm $JLINK_SCRIPT
