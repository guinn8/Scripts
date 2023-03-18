#!/bin/bash

# Copyright (c) 2023 Simply Embedded Inc.
# All Rights Reserved.
#
# File: gdb_connect.sh
# Brief: Launches gdb server and connects to it, reads uart tty output
# args:
#   AXF_FILE: Load symbols from this file

AXF_FILE=$1

GDB_FILE=~/Scripts/device.gdb
TTY_DEV=/dev/ttyACM0

# TODO(Gavin): The sleep wait for the gdb server to init
tmux new-session -d "sleep 2 && arm-none-eabi-gdb $AXF_FILE -x $GDB_FILE -q"
tmux set remain-on-exit on

tmux split-window -v " killall screen || true && screen $TTY_DEV 115200"
tmux resize-pane -t 1 -y 10
tmux set remain-on-exit on

# https://wiki.segger.com/J-Link_GDB_Server#Command_line_options
tmux split-window -h -f "source ~/Scripts/gdb_server.sh"
tmux resize-pane -t 2 -x 20
tmux set remain-on-exit on

tmux select-pane -t 0
tmux set remain-on-exit on

###
# Exit: exit this script with the key-chord `contrl - b` (command mode) then `control-x` (exit), then press `y` for yes.
#
# Copy: left click and drag to highlight text in yellow then press `enter` to copy 
###
tmux set -g mouse on
tmux bind X confirm-before kill-session

tmux bind -n WheelUpPane if-shell -F -t = "#{mouse_any_flag}" "send-keys -M" "if -Ft= '#{pane_in_mode}' 'send-keys -M' 'select-pane -t=; copy-mode -e; send-keys -M'"
tmux bind -n WheelDownPane select-pane -t= \; send-keys -M
tmux bind -n C-WheelUpPane select-pane -t= \; copy-mode -e \; send-keys -M
tmux bind -T copy-mode-vi    C-WheelUpPane   send-keys -X halfpage-up
tmux bind -T copy-mode-vi    C-WheelDownPane send-keys -X halfpage-down
tmux bind -T copy-mode-emacs C-WheelUpPane   send-keys -X halfpage-up
tmux bind -T copy-mode-emacs C-WheelDownPane send-keys -X halfpage-down

tmux setw -g mode-keys vi
tmux unbind -T copy-mode-vi Enter
tmux bind-key -T copy-mode-vi Enter send-keys -X copy-pipe-and-cancel "xclip -selection c"
tmux bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel "xclip -in -selection clipboard"

tmux -2 attach-session -d 