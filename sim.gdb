define quiet-on
    set logging file /dev/null
    set logging redirect on
    set logging enabled on
end

define quiet-off
    set logging enabled off
end

# b _system_task

set pagination off
quiet-on

run

set pagination on
quiet-off
