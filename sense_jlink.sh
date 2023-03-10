#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJ_BASE=`realpath $SCRIPT_DIR/../..` # !! NEEDS MODIFICATION IF MOVED !!
CMD_FILE=$1

echo $CMD_FILE

JLinkExe -Si swd -speed auto -AutoConnect 1 -Device MIMXRT1021XXX5A -CommandFile $CMD_FILE -NoGui 1