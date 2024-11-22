#!/bin/bash
Xvfb :99 -ac -screen 0 "$XVFB_RES" -nolisten tcp &
XVFB_PROC=$!
sleep 2
echo $DISPLAY
python3 scripts/main.py
kill $XVFB_PROC
