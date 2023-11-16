define gi
    j *0x6010499d
end

define app
    j *0x6080499d
end

 
target remote localhost:2331
set mem inaccessible-by-default off

set {int}0x400AC044=0
set {int}0x400AC040=0x00200003
set {int}0x400AC038=0x00aa0000
monitor reset
c
