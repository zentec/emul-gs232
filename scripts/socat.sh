#!/bin/bash
#
# creates a virtual serial cable between /dev/ttyS10 and /dev/ttyS11
#
sudo socat -d -d pty,link=/dev/ttyS10,raw,echo=0 pty,link=/dev/ttyS11,raw,echo=0
