import os
import sys
import random
import time
import threading

'''  emul-gs232.py by ka8ncr  '''
'''  MIT license              '''


try:
    import RPi.GPIO as GPIO
except:
    GPIO = None

class GPIORelay:
    def __init__(self,conf,debug):
        self.debug = debug
        if debug:
            print(f"GPIORelay: initialize GPIORelay")
        if GPIO == None:
            print("Can't initialize GPIO module (missing) ... soldiering on")
            return None
        self.conf = conf
        self.relays = {"RELAY1":15,"RELAY2":13,"RELAY3":11,"RELAY4":7}
        try:
            GPIO.setmode(GPIO.BOARD)
            for key,val in self.relays.items():
                GPIO.setup(val, GPIO.OUT)
                GPIO.output(val, GPIO.LOW)
        except:
            print("Can't initialize relays, check GPIO permissions or set up UDEV rule")
            return None

        self.relay1 = self.Relay(self.relays['RELAY1'],GPIO)
        self.relay2 = self.Relay(self.relays['RELAY2'],GPIO)
        self.relay3 = self.Relay(self.relays['RELAY3'],GPIO)
        self.relay4 = self.Relay(self.relays['RELAY4'],GPIO)
        self.up = self.Relay(self.relays[conf['up']],GPIO)
        self.down = self.Relay(self.relays[conf['down']],GPIO)
        self.cw = self.Relay(self.relays[conf['cw']],GPIO)
        self.ccw = self.Relay(self.relays[conf['ccw']],GPIO)


    class Relay:
        def __init__(self,chan,gpio):
            self.gpio = gpio
            self.chan = chan
        def on(self):
            GPIO.output(self.chan,self.gpio.HIGH)
        def off(self):
            GPIO.output(self.chan,self.gpio.LOW)


class RelayPositioner:
    def __init__(self,config,resolver,debug):
        self.debug = debug
        if self.debug:
            print(f"RelayPositioner: initialize RelayPositioner")
        self.relay = GPIORelay(config['relays'],self.debug)
        self.config = config
        self.az_thread_stop = False
        self.el_thread_stop = False
        self.el_timeout = config['el_timeout'] or 20
        self.az_timeout = config['el_timeout'] or 20
        self.az_pos = 0
        self.el_pos = 0
        self.resolver = resolver


    def get_requested_az(self):
        return self.az_pos

    def get_requested_el(self):
        return self.el_pos
 
    def stop(self):
        for run_queue in threading.enumerate():
            if run_queue.getName() == 'az_position_thread':
                self.az_thread_stop = True
            if run_queue.getName() == 'el_position_thread':
                self.el_thread_stop = True
        self.az_stop()
        self.el_stop()

    def az_stop(self):
        if self.relay is not None:
            self.relay.cw.off()
            self.relay.ccw.off()

    def el_stop(self):
        if self.relay is not None:
            self.relay.up.off()
            self.relay.down.off()

    def move_ccw(self):
        if self.relay is not None:
            self.relay.cw.off()
            self.relay.ccw.on()

    def move_cw(self):
        if self.relay is not None:
            self.relay.ccw.off()
            self.relay.cw.on()

    def move_up(self):
        if self.relay is not None:
            self.relay.down.off()
            self.relay.up.on()

    def move_down(self):
        if self.relay is not None:
            self.relay.up.off()
            self.relay.down.on()
    '''
       set_position: sets the class data for the desired az/el position and launches threads to do the work
    '''

    def set_position(self,az,el):
        az_positioner = False
        el_positioner = False
              
        if az != self.az_pos:
             self.az_pos = az
        if el != self.el_pos:
             self.el_pos = el

        for run_queue in threading.enumerate():
            if run_queue.getName() == 'az_position_thread':
                az_positioner = True
            if run_queue.getName() == 'el_position_thread':
                el_positioner = True
        if not az_positioner:
            positioner_thread = threading.Thread(name='az_position_thread',target=self.drift_positioner,args=(self.get_requested_az,self.resolver.get_az,self.move_ccw,self.move_cw,self.az_stop,self.az_timeout,self.az_thread_stop))
            positioner_thread.start()
        if not el_positioner:
            positioner_thread = threading.Thread(name='el_position_thread',target=self.drift_positioner,args=(self.get_requested_el,self.resolver.get_el,self.move_down,self.move_up,self.el_stop,self.el_timeout,self.el_thread_stop,))
            positioner_thread.start()
        
    '''
       drift_positioner: function to run as a thread that will activate either az or el relays to move the motors

       def_get_request = a function of az/el that returns the currently requested postion
       def_get_postion = a function that returns the current az/el postion
       def_low         = a function that moves the motor in the low direction (down for el, ccw for az)
       def_high        = a function that moves the motor in the high direction (up for el, cw for az)
       def_stop        = a function that stops the currently running motor
       def timeout     = an integer value that specifies the limit a thread may run
       def stop_flag   = bool flag to interrupt a running thread
    '''

    def drift_positioner(self,def_get_request,def_get_position,def_low,def_high,def_stop,timeout,stop_flag):
        t = time.time()
        if int(def_get_request()) <  int(def_get_position()):
             while (int(def_get_request()) < int(def_get_position())) and (time.time() - t) < timeout and stop_flag is False:
                  def_low()
                  time.sleep(.2)
             def_stop()
                  
        else:
             while (int(def_get_request()) > int(def_get_position())) and (time.time() -t) < timeout and stop_flag is False:
                 def_high()
                 time.sleep(.2)
             def_stop()

