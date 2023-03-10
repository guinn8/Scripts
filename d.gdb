define quiet-on
    set logging file /dev/null
    set logging redirect on
    set logging on
end

define quiet-off
    set logging off
end


define load-quiet
    quiet-on
    load
    quiet-off
end

define reload
    make -C $PROJ_BASE id-app -j
    load-quiet
    reset
end

target remote localhost:2331
set mem inaccessible-by-default off
set pagination off
#load-quiet
#b main

set {int}0x400AC044=0
set {int}0x400AC040=0x00200003
set {int}0x400AC038=0x00aa0000
monitor reset
set pagination on