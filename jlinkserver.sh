#!/bin/bash
JLinkGDBServerCLExe \
    -select USB \
    -endian little\
    -speed auto \
    -device MIMXRT1021XXX5A \
    -if SWD \
    -rtos GDBServer/RTOSPlugin_FreeRTOS \
    -halt -vd -noir -singlerun

