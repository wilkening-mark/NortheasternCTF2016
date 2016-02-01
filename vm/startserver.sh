#!/usr/bin/env bash

socat -v tcp-listen:5000 tcp-connect:localhost:9500 &
python server.py &
nc 192.168.7.2 6000
