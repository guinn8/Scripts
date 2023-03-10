#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJ_BASE=`realpath $SCRIPT_DIR/../..` # !! NEEDS MODIFICATION IF MOVED !!
export CROSS_COMPILE=
export TARGET=sim
export BUILD_FLAG=debug

make -C $PROJ_BASE id-app -j
if [ $? == 0 ]; then
    printf "\nCompilation success!\n\n"
else
    printf "\nCompilation fail, exiting...\n\n"
    exit 1
fi

sudo gdb $PROJ_BASE/build/sim/bin/sense-id.axf -x $SCRIPT_DIR/sim.gdb -q
