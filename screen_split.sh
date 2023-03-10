#!/bin/bash

screen -d -m -S debug
screen -S debug -p 1 -X stuff $'bash gdbconnect.sh\n'