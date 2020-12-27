
#!/usr/bin/env python3

import argparse
import serial
import sys
import yaml

'''
  emul-gs232.py by ka8ncr
  MIT license.

  Each one of these functions is passed a list of arguments, with element 0 a list containing
  the positioner and resolver objects

  The list of objects and variables was chosen because these functions get called from a dictionary
  object with its key the command coming in on the serial port

  Required class functions for positioner:
    stop()
    az_stop()
    el_stop()
    move_ccw()
    move_cw()
    move_up()
    move_down()
    set_position()

  Required class functions for resolver:
    get_el()
    get_az()


'''

def return_azel_position(args):
    ret = 'AZ=' + str(int(args[0][1].get_az())).zfill(3) + 'EL=' + str(int(args[0][1].get_el())).zfill(3)
    return ret + '\r'

def stop_motion_all(args):
    args[0][0].stop()
    return '\r'

def stop_motion_azimuth(args):
    args[0][0].az_stop()
    return '\r'

def return_elevation(args):
    return 'EL=' + str(int(args[0][1].get_el())).zfill(3) + '\r'

def return_azimuth(args):
    return 'AZ=' + str(int(args[0][1].get_az())).zfill(3) + '\r'

def move_ccw(args):
    args[0][0].move_ccw()
    return '\r'

def move_cw(args):
    args[0][0].move_cw()
    return '\r'

def move_up(args):
    args[0][0].move_up()
    return '\r'

def move_down(args):
    args[0][0].move_down()
    return '\r'

def move_to_position(args):
    args[0][0].set_position(args[1][0],args[1][1])
    return '\r'

def move_single_axis(args):
    return '\r'

def set_speed_high(args):
    return '\r'

def parse_yaml(f):
	with open(f,'r') as yamlfile:
		try:
			return yaml.load(yamlfile)
		except:
			print("Can't open {0}".format(args['config']))
			sys.exit(1)
'''
   A dictionary containing the function to be called is assembled here, with the key of the dict 
   being the command coming in on the wire.
'''
def process_request(command,sp,positioner,resolver,debug = False):
    handlers = []
    cmd = {
            "C2":return_azel_position,
            "S":stop_motion_all,
            "B":return_elevation,
            "E":stop_motion_azimuth,
            "D":move_ccw,
            "U":move_cw,
            "W":move_to_position,
            "X1":move_single_axis,
            "L":move_down,
            "R":move_up,
            "X4":set_speed_high
          }
    handlers.append(positioner)
    handlers.append(resolver)
    if debug:
        print(f"main::process_request:Handling input command {command}")
    args = []
    args.append(handlers)
    if command in cmd:
        func = cmd[command]
        ret = func(args)
        if len(ret) > 0:
            sp.write(ret.encode())
    else:
        func = cmd[command[0]]
        a = command[1:].split()
        args.append(a)
        ret = func(args)
        if len(ret) > 0:
            sp.write(ret.encode())

            

def open_serial(port_cfg):
        sp = serial.Serial(port_cfg['device'],port_cfg['baud'],timeout=1)
        try:
            sp.is_open
        except SerialException:
            print("Can't read %s" % port_cfg['device'])
            sys.exit(1)
        return(sp)

def serial_handler(sp,positioner,resolver,debug=False):
    ''' reads serial port '''
    buffer = ""
    while True:
        line = ""
        try:
            ch = sp.read()
            if ch != b'\r':
                if len(ch.decode('utf-8')) > 0:
                    buffer = buffer + ch.decode('utf-8')
            else:
                if debug:
                    print(f"main::serial_handler: {buffer}")
                process_request(buffer,sp,positioner,resolver,debug)

                buffer = ""
            #.decode('utf-8')
        except Exception as e:
            print(f"serial_handler exception {e}")
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gs-232B Python Emulator')
    parser.add_argument("-c", "--config", required=True,
        help="YAML Config")
    parser.add_argument("-d", "--debug", required=False, default=False, action='store_true',
        help="Debug Logging")
    args = parser.parse_args()

    yaml_config = parse_yaml(args.config)

    ''' this loads up a resolver object ... it is rquired to pass to the positioner '''
    resolver_config = yaml_config['resolver']
    resolver_module = __import__(resolver_config['module'])
    resolver_class = getattr(resolver_module, resolver_config['class'])
    resolver = resolver_class(yaml_config[resolver_config['config']],args.debug)

    ''' load up a positioner, pass it the above resolver '''
    positioner_config = yaml_config['positioner']
    positioner_module = __import__(positioner_config['module'])
    positioner_class = getattr(positioner_module, positioner_config['class'])
    positioner = positioner_class(yaml_config[positioner_config['config']],resolver,args.debug)

    ''' open serial port configred in yaml file, begin reading the port for driver commands '''
    sp = open_serial(yaml_config['serial'])
    serial_handler(sp,positioner,resolver,args.debug)


