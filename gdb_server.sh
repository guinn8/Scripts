#!/bin/bash

# Copyright (c) 2023 Simply Embedded Inc.
# All Rights Reserved.
#
# File: gdb_server.sh
# Brief: Launches gdb server

killall JLinkGDBServerCLExe
JLinkGDBServerCLExe -select USB \
                    -endian little \
                    -speed auto \
                    -device MIMXRT1021XXX5A \
                    -if SWD \
                    -rtos GDBServer/RTOSPlugin_FreeRTOS \
                    -halt -vd -noir -nogui\
                    -singlerun