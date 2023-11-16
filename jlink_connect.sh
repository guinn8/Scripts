#!/bin/bash

# Copyright (c) 2023 Simply Embedded Inc.
# All Rights Reserved.
#
# File: jlink_connect.sh
# Brief: Connects to device over JLink
# args:
#   CMD_FILE: Execute JLink commandfile if supplied
#   DEV_ID (optional): device id (default MIMXRT1021XXX5A)

CMD_FILE=$1
DEV_ID=${2:-MIMXRT1021XXX5A}  # default to MIMXRT1021XXX5A if not provided
if [ -z "$CMD_FILE" ] 
    then
        JLinkExe -Si swd -speed adaptive -AutoConnect 1 -Device $DEV_ID -NoGui 1
    else
        JLinkExe -Si swd -speed 16000 -AutoConnect 1 -Device $DEV_ID -CommandFile $CMD_FILE -NoGui 1
fi