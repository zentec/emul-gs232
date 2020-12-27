# emul-gs232
Raspberry Pi GS-232B Satellite Controller Protocol Emulator

## Overview

This is a Python framework for emulating the GS-232B satellite tracking protocol and providing handlers for positioners and resolvers.  It is primarily intended to run on Raspberry Pi computers and interface with third-party relay boards and analog to digital converters.

The main program pulls in Python classes and calls those member functions when receving command calls, allowing for custom positioner and resolvers to be used while maintaining the same GS-232B protocol handler.

Tested With Tracker/Driver Programs
* MacDoppler 2.38 beta3
* Gpredict via Hamlib rotctl


## Why This?

This work was born out of the need to interface MacDoppler to a couple second or third hand rotors and a few devices never intended to run as AZ/EL rotors (such as industrial grade pan/tilt heads).  My use case was to utilize the parts on hand, which meant a Raspberry Pi and the few boards (or hats) I had available.


## Getting Started

As cloned, this repo will provide resources to interface to an emulated AZ/EL rotor setup, a 4 port relay board, a 4 channel DIO ADC and a Wit motion accelerometer.  It assumes that whatever drives the program is relatively compliant with the GS-232B protocol.

If using a serial port to drive the program, it will need to be done with a null modem cable.  The program does not use hardware handshaking, so a null modem adapter should be simple to construct.  If interfacing via hamlib, the rotctl daemon can be run on the same computer and virtual serial ports used to interface to the main program.  Examples are in the scripts directory.

When using multiple serial devices over USB, it may be helpful to apply UDEV rules so the ports can be predicably found.

### Configuration

All configuration is via YAML files.  The main program needs to be indstructed which resolver to use, and which positioner to use.  Included in those configuration blocks are the titles of the configs for those modules.

### Command Line Parameters

emul-232.py requires one command line variable, -c or --config to name the YAML config file to use.  Optionally, -d or --debug can be used to output debug information.

### Test Drive

The repo contains a test positioner and a test resolver, stubpositioner.py and stubresolver.py.  Stubposition has a thread that emulates the interfacing to a real rotor in /dev/shm.  Commands are written as zero byte files, the thread sees these and acts appropriately moving an imaginary AZ/EL rotor.  The result is stored in /dev/shm as well, making restarting from a test point a bit easier.

If a common relay board is inserted on a Raspberry PI's GPIO pins, the module *should* be able to move those relays.

## Using in Real Life

Controlling a real rotor will require interfacing a positioner class to some hardware.

### Yaesu G-5500 AZ/El Rotor

The use case here is to avoid having to buy the G-232B interface board.  This works, but in addition to a relay board to provide contact closures, there will also need to be some sort of analog to digital board for reading the positioner pots.  Resolver ads_1115_resolver.py does this with the following important caveats:

* The Raspberry Pi I2C buss is 3.3 volts, while the output of the controller box of the G-5500 is 5 volts.  This will require a voltage divider (two resistors, each 10K should work).
* WHERE you obtain your ads_115 board might be important.  The module is written for the Adafruit libraries, and even though it will likely work with the garbage Pi accessories found on the internet, be prepared for fun.  Plus, Adafruit Industries is run by an amateur radio operator, so there is that.
* There may need to be some code changes in the positioner board depending upon the resolution out of the voltage divider.  Start with the relaypositioner.py and go from there.

### Pan Tilt Heads

This is one of the test cases.  Use the relaypositioner.py to drive the pan/tilt head, but the resolver depends on the pan/tilt head.  Resistive resolution might be able to use the ads_1115_resolver.py, optical encoders will need to be written from scratch.  If added expense is not an issue, there is a Wit Motion resolver that works reasonably well, although the GPS model might be a better idea.

### Alfa-Spid

You have an Alfa-Spid?  Neat!









