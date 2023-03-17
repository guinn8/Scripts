source ~/Scripts/jlink_load.sh bootloader/build/proto-d/bin/bootloader.hex 0x60000000
source ~/Scripts/jlink_load.sh build/proto-d/bin/sense-gi-signed.bin 0x60100000
source ~/Scripts/jlink_load.sh build/proto-d/bin/sense-id-signed.bin 0x60800000
