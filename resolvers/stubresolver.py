import os
import sys
import time

'''  emul-gs232.py by ka8ncr  '''
'''  MIT license              '''


class StubResolver:
    def __init__(self,config,debug = False):
        if debug:
            print(f"initialize StubResolver")
        self.config = config
        self.up = config['up']
        self.down = config['down']
        self.cw = config['cw']
        self.ccw = config['ccw']
        self.el = config['el_out']
        self.az = config['az_out']
        self.az_v_multiplier = config['az_v_multiplier']
        self.el_v_multiplier = config['el_v_multiplier']
        self.el_v_correction = config['el_v_correction']
        self.az_v_correction = config['az_v_correction']
        self.az_max = config['az_max']
        self.el_max = config['el_max']
        self.az_pos = 0
        self.el_pos = 0

    def get_az(self):
        az = -1
        if os.path.exists(self.az):
            with open(self.az,"r") as azread:
                try:
                   az = float(azread.readline())
                except:
                   az = -1
        return az

    def get_el(self):
        el = -1
        if os.path.exists(self.el):
            with open(self.el,"r") as elread:
                try:
                    el = float(elread.readline())
                except:
                    el = -1
        return el

