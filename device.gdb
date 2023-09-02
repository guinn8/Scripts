define gi
    j *0x6010499d
end


target remote localhost:2331
set mem inaccessible-by-default off

set {int}0x400AC044=0
set {int}0x400AC040=0x00200003
set {int}0x400AC038=0x00aa0000
monitor reset
c

#python
# Update GDB's Python paths with the `sys.path` values of the local
#  Python installation, whether that is brew'ed Python, a virtualenv,
#  or another system python.

# Convert GDB to interpret in Python
#import os,subprocess,sys
# Execute a Python using the user's shell and pull out the sys.path (for site-packages)
#paths = subprocess.check_output('python2.7 -c "import os,sys;print(os.linesep.join(sys.path).strip())"',shell=True).decode("utf-8").split()
# Extend GDB's Python's search path
#sys.path.extend(paths)
#end
