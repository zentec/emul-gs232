#!/bin/bash
#
# this will operate rotctld for use with Gpredict on the Pi through a virtual serial port
# make sure to run the socat script *first*
sudo rotctld -C post_write_delay=700 -C timeout=900 -vvvvvvv -m 603 -s 57600 -r /dev/ttyS11
