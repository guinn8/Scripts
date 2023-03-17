#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PROJ_BASE=`realpath $SCRIPT_DIR/../..` # !! NEEDS MODIFICATION IF MOVED !!
# CMD_FILE=~/Scripts/temp.jlink
CMD_FILE=$1
DEV_ID=MIMXRT1021XXX5A

if [ -z "$CMD_FILE" ] 
    then
        JLinkExe -Si swd -speed auto -AutoConnect 1 -Device $DEV_ID -NoGui 1
    else
        JLinkExe -Si swd -speed auto -AutoConnect 1 -Device $DEV_ID -CommandFile $CMD_FILE -NoGui 1
fi