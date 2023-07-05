python
import gdb
import os

class GiCommand(gdb.Command):
    "Implements the 'gi' command."

    def __init__(self):
        super(GiCommand, self).__init__("gi", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        PROJ_ROOT="/home/guinn8/SimplyEmbedded/human-id"
        CROSS_COMPILE="arm-none-eabi-"
        TARGET="proto-d"
        
        # Running the make command
        os.system('CROSS_COMPILE={} TARGET={} make -C {}/bootloader -j'.format(CROSS_COMPILE, TARGET, PROJ_ROOT))
        
        gdb.execute("monitor reset")
        gdb.execute("file {}/bootloader/build/proto-d/bin/bootloader.axf".format(PROJ_ROOT))
        gdb.Breakpoint("{}/bootloader/main.c:134".format(PROJ_ROOT))
        gdb.execute("continue")
        gdb.execute("set confirm off")
        gdb.execute("jump *gi_reset_vector")
        gdb.execute("set confirm on")
        gdb.execute("file {}/build/proto-d/bin/sense-gi-cli.axf".format(PROJ_ROOT))

GiCommand()
end


target remote localhost:2331
set mem inaccessible-by-default off

set {int}0x400AC044=0
set {int}0x400AC040=0x00200003
set {int}0x400AC038=0x00aa0000
monitor reset

python
# Update GDB's Python paths with the `sys.path` values of the local
#  Python installation, whether that is brew'ed Python, a virtualenv,
#  or another system python.

# Convert GDB to interpret in Python
import os,subprocess,sys
# Execute a Python using the user's shell and pull out the sys.path (for site-packages)
paths = subprocess.check_output('python2.7 -c "import os,sys;print(os.linesep.join(sys.path).strip())"',shell=True).decode("utf-8").split()
# Extend GDB's Python's search path
sys.path.extend(paths)
end

