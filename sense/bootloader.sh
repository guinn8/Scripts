CROSS_COMPILE=arm-none-eabi- TARGET=proto-d make -C bootloader -j

# Exit if compilation fails
if [ $? == 0 ]; then
    printf "\nCompilation success!\n\n"
else
    printf "\nCompilation fail, exiting...\n\n"
    exit 1
fi

source ~/Scripts/jlink_load.sh bootloader/build/proto-d/bin/bootloader.hex 0x60000000
source ~/Scripts/gdb_connect.sh bootloader/build/proto-d/bin/bootloader.axf