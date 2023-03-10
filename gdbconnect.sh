#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export EXECUTABLE="/home/guinn8/Code/human-id/build/proto-d/bin/sense-id.axf"
export GDB_SCRIPT=$SCRIPT_DIR/gdb/remote.gdb

arm-none-eabi-gdb $EXECUTABLE -x $GDB_SCRIPT -q
