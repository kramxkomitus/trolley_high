#!/bin/bash
for KILLPID in `ps ax | grep gamepad_server | awk ‘{print $1;}’`; do
kill -9 $KILLPID;
done