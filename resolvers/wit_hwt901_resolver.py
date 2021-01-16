#!/usr/bin/env python3

'''  emul-gs232.py by ka8ncr  '''
'''  MIT license              '''


import argparse
import serial
import sys
import threading
import time
import yaml

class Wit_HWT901_Resolver:
    def __init__(self,config = None, debug = False):
        self.config = config
        self.x = 0
        self.y = 0
        self.z = 0
        self.sp = None
        self.th_serial = None
        self.run = False
        self.start()
        

    def start(self):
        self.sp = self.open_serial(self.config)
        self.run = True
        try:
            self.th_serial = threading.Thread(name='serial_handler',target=self.serial_handler,args=(self.sp,))
            self.th_serial.start()
        except Exception as e:
            print(e)

    def stop(self):
        self.run = False
        self.th_serial.join()
        self.sp.close()

    def get_az(self):
         return round(self.y, 4)

    def get_el(self):
        ''' this function is likely not what you want, test and adapt to your own hardware '''
        if self.x > 180:
            return round(180 - self.x,4)
        return round(self.x,4)

    def open_serial(self, config = None):
        if config == None:
            return False
        sp = serial.Serial(config['port'],config['baud'],timeout=1)
        try:
            sp.is_open
        except SerialException:
            return False
        return(sp)

    def serial_handler(self, sp):
        while self.run == True:
            byte = sp.read()
            if byte == b'\x55':
                byte = sp.read()
                if byte == b'\x53':
                    data_frame = sp.read(9)
                    checksum = 168
                    for n in range(0,8):
                        checksum = checksum + data_frame[n]
                    checksum = checksum & 0xFF
                    if checksum == data_frame[8]:
                        self.x = round( ((data_frame[1] << 8|data_frame[0])/32768*180), 1)
                        self.y = round( ((data_frame[3] << 8|data_frame[2])/32768*180), 1)
                        self.z = round( ((data_frame[5] << 8|data_frame[4])/32768*180), 1)
            

if __name__ == "__main__":
    """ command line testing """
    config = {}
    config['port'] = '/dev/ttyUSB0'
    config['baud'] = 9600
    resolver = Wit_HWT901_Resolver(config)
    #print("starting thread")
    #resolver.start()
    for n in range(300):
        print(f"x:{resolver.x} y:{resolver.y} z:{resolver.z}")
        print(f"el:{resolver.get_el()} az:{resolver.get_az()}")
        time.sleep(1)
    print("ending thread")
    resolver.stop()

