#!/bin/sh

adb start-server
if [ $# -eq 0 ]; then
    exec tail -f /dev/null
else
    exec "$@"
fi 