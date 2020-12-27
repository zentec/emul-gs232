'''
   emul-gs232.py by ka8ncr
   MIT license         

  Resolver using the Adafruit ADS1115 to read the G-500 rotor controller output

  Note that the Raspberry PI is a 3.3 volt system, and the easiest way to avoid
  toasting the ADC and perhaps the PI I2C buss is to use a voltage divider on the
  2 -> 4.5 volts coming from the controller
'''

import time
import Adafruit_ADS1x15

class Ads1115Resolver:
    def __init__(self, config, debug = False):
        self.gain = config['gain'] or 1
        self.address = config['address'] or 0x48
        self.i2c_buss = config['i2c_bus'] or 1
        self.az = config['az_channel']
        self.el = config['el_channel']
        self.az_voltage = 0
        self.el_voltage = 0
        self.el_multiplier = config['el_v_multiplier']
        self.el_correction = config['el_v_correction']
        self.az_multiplier = config['az_v_multiplier']
        self.az_correction = config['az_v_correction']
        try:
            adc = Adafruit_ADS1x15.ADS1115(self.address,self.i2c_buss)
        except:
            print("Can't open I2C buss object")
        adc.start_adc(self.az,self.gain)
        adc.start_adc(self.el,self.gain)
     
    def start_threads(self):
        noop = noop

    def get_az(self):
        return (self.az_voltage * 

    def get_el(self):
        noop = noop



GAIN = 2

adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)

adc.start_adc(3, gain=GAIN)

print('Reading ADS1x15 channel 0 for 5 seconds...')
start = time.time()
while (time.time() - start) <= 5.0:
    # Read the last ADC conversion value and print it out.
    value = adc.get_last_result()
    # WARNING! If you try to read any other ADC channel during this continuous
    # conversion (like by calling read_adc again) it will disable the
    # continuous conversion!
    print('Channel 0: {0}'.format(value))
    # Sleep for half a second.
    time.sleep(0.5)

# Stop continuous conversion.  After this point you can't get data from get_last_result!
adc.stop_adc()
