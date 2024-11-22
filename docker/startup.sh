#!/bin/bash
Xvfb :99 -ac -screen 0 "$XVFB_RES" -nolisten tcp $XVFB_ARGS &
XVFB_PROC=$!
sleep 1
export DISPLAY=:99
python3 scripts/main.py
kill $XVFB_PROC
