#!/usr/bin/env python3
import os
#import OPi.GPIO as GPIO
import socket
import signal
import textwrap
from daemon import DaemonContext, pidfile
import logging
import argparse
import importlib.util
import sys
import grp as groups
import json
import yaml
"""
Error codes:
2  -  No such file or directory.
3  - No such process.
22 - Misconfigured. Invalid arguments and stuff.
"""

settings_location = "./settings.py"
"""
### This is a debugging stub for developing on a desktop


class gpio():

    def setmode(self, mode):
        print(mode)

    SUNXI = "SUNXI"
    BCM = "BCM"
    BOARD = "BOARD"
    OUT = "OUT"

    def setup(self,pin, mode):
        print("Pin: ", pin, " Mode:", mode)


    def output(self, pin, output):
        print("Pin: ", pin, " State:", output)


GPIO = gpio()
#"""
positive_state = ["on", "true", "up"]
negative_state = ["off", "false", "down"]
######## Importing settings ###################
spec = importlib.util.spec_from_file_location("settings", settings_location)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.modules["settings"] = module
try:
    import settings
except ImportError:
    print("[!] No settings in {location}".format(location=settings_location))
    exit(2)



def control(connection, thing_to_control, command):
    """

    :param connection:
    :param thing_to_control:
    :param command:
    :return:

    """
    if thing_to_control in settings.PINS:
        # So, we have a pin

        if command in positive_state:
            GPIO.output(thing_to_control, True)

        if command in negative_state:
            GPIO.output(thing_to_control, False)
        # try:
        #     connection.sendall(b"Success\n")
        # except BrokenPipeError:
        #     pass

        return True

    elif thing_to_control in settings.ALIASES.values():
        # It's no ta pin. Maybe alias?

        verified_pin = None
        for pin, alias in settings.ALIASES.items():
            if thing_to_control == alias:
                verified_pin = pin

        if command in positive_state:
            GPIO.output(verified_pin, True)

        if command in negative_state:
            GPIO.output(verified_pin, False)

        # try:
        #     connection.sendall(b"Success\n")
        # except BrokenPipeError:
        #     pass

        return True

    return False


def main(logf):
    """

    :param logf:
    :return:
    """

    logger = logging.getLogger('opid')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logf)
    fh.setLevel(logging.INFO)
    formatstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formatstr)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, )

    if settings.GPIO_MODE == "SUNXI":
        GPIO.setmode(GPIO.SUNXI)

    elif settings.GPIO_MODE == "BCM":
        GPIO.setmode(GPIO.BCM)

    elif settings.GPIO_MODE == "BOARD":
        GPIO.setmode(GPIO.BOARD)

    else:
        logger.error("Unknown GPIO_MODE specified!")
        print("Unknown GPIO_MODE specified!", file=sys.stderr)
        exit(22)  # define EINVAL 22 /* Invalid argument */

    for pin in settings.PINS:
        GPIO.setup(pin, GPIO.OUT)
    try:
        os.unlink(settings.SOCKET)
    except OSError:
        if os.path.exists(settings.SOCKET):
            raise

    sock.bind(settings.SOCKET)
    opid_uid = 1000
    opid_gid = 1000
    try:
        """
        In orfer to get our GID, we need to get all groups and parse only our needed one.
        """

        groups_list = groups.getgrall()
        for group in groups_list:
            if group.gr_name == settings.GROUP:
                opid_gid = group.gr_gid
        del groups_list

        """
        Writinbg to GPIO requires root permissions. 
        Dunno how to fix this wothout writing a kernel patch :)
        So we need to run this daemon as root. But group is usable for socket. 
        """
        os.chown(settings.SOCKET, opid_uid, opid_gid)
    except OSError as error:
        logger.error("Failed to change socket permissions. UID: {uid}, GID:{gid}".format(uid=opid_uid,
                                                                                         gid=opid_gid))
        logger.error(error.strerror)
        exit(error.errno)

    sock.listen(1)
    logger.info('Started OPID Daemon')

    while True:
        # Wait for a connection

        logger.info('Waiting for connection')
        connection, client_address = sock.accept()
        try:
            # Receive the data in chunks and parse it.
            """
            Notation: <PIN/ALIAS> <STATE>
            Pin can be described in any of desired GPIO_MODES? if it was previously set in settings.
            PIN/ALIAS is case sensitive!
             
            State: up/true/on or down/false/off
            
            """

            orders = []
            """
            ^ It's a list of dicts with folowing notation:
            [
                {
                    'thing_to_control': "PA14",
                    'command':          "Off"
                },
                {
                    'thing_to_control': "Magic_Lamp",
                    'command':          "On"
                }
            ]
            """
            stored_data = b''
            data = None
            while True:
                data = connection.recv(16)
                if data:
                    stored_data += data
                else:
                    break
            if stored_data:
                data = stored_data.decode("utf-8")
            else:
                break
            # Default command notation
            if settings.COMMAND_FORMAT == "SEMANTIC":
                data = data.rstrip()
                rez = data.split(" ")

                if len(rez) == 1:
                    # If we have only "\n"
                    break

                data = list(filter(None, rez))
                thing_to_control = data[0]
                command = data[1].lower()
                orders.append({
                    'thing_to_control': thing_to_control,
                    'command': command
                })

            elif settings.COMMAND_FORMAT == "YAML":
                """
                Notaton:
                --- 
                devices:
                    - pin: PA14
                      state: False
                    = pin: Magic_Lamp
                      state: On
                """
                raw_orders = yaml.load(data)
                raw_orders = raw_orders
                for order in raw_orders['devices']:
                    orders.append({
                        'thing_to_control': order['pin'],
                        'command': order['state']
                    })

            elif settings.COMMAND_FORMAT == "JSON":
                """
                Notation:
                {
                 "devices": [
                    { 
                        "pin": "PA14",
                        "state": "False"
                    },
                    {
                        "pin": "Magic_Lamp",
                        "state": "On"
                    }
                 ] 
                }
                """
                raw_orders = json.loads(data)
                for order in raw_orders['devices']:
                    orders.append({
                        'thing_to_control': order['pin'],
                        'command': order['state']
                    })

            for order in orders:

                if control(connection, order['thing_to_control'], order['command']):
                    logger.info("Pin: {pin} State: {state}".format(pin=order['thing_to_control'],
                                                                   state=order['command']))
                else:
                    # Connection got closed somehow.
                    logger.error('Unrecognized command')
                    logger.error("Pin: {pin} State: {state}".format(pin=order['thing_to_control'],
                                                                   state=order['command']))
                    try:
                        connection.sendall(b"\nUnrecognized command\n")
                    except BrokenPipeError:
                        pass

        finally:
            # Clean up the connection
            logger.info("Closing conn")
            connection.close()


def cleanup():
    os.remove(settings.PID_FILE)
    os.remove(settings.SOCKET)
    os.rmdir(settings.RUN_FILES)
    try:
        os.unlink(settings.SOCKET)
    except OSError:
        if os.path.exists(settings.SOCKET):
            raise
    return


def start_daemon():
    if not os.path.isdir(settings.RUN_FILES):
        os.makedirs(settings.RUN_FILES, exist_ok=True)
    daemon_context = DaemonContext(
            working_directory=settings.RUN_FILES,
            umask=settings.UMASK,
            pidfile=pidfile.TimeoutPIDLockFile(settings.PID_FILE),
        )

    daemon_context.signal_map = {
        signal.SIGTERM: cleanup,
        signal.SIGHUP: 'terminate',
    }

    with daemon_context:
        main(settings.LOG_FILE)


def stop_daemon():
    try:
        pid = int(open(os.path.join(settings.RUN_FILES, settings.PID_FILE)).read())
        os.kill(int(pid), signal.SIGTERM)
    except FileNotFoundError:
        print("Daemon seems to be dead/stopped...")
        exit(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'opid',formatter_class = argparse.RawDescriptionHelpFormatter,
                                     description = textwrap.dedent('''
    =======================================
                                                        
      ,ad8888ba,    88888888ba   88  88888888ba,    
     d8"'    `"8b   88      "8b  88  88      `"8b   
    d8'        `8b  88      ,8P  88  88        `8b  
    88          88  88aaaaaa8P'  88  88         88  
    88          88  88""""""'    88  88         88  
    Y8,        ,8P  88           88  88         8P  
     Y8a.    .a8P   88           88  88      .a8P   
      `"Y8888Y"'    88           88  88888888Y"'    
                                                        
    =======================================
    For Orange Pi gpio Daemon
    '''))
    parser.add_argument('-p', '--stop', action='store_const', const=True)
    parser.add_argument('-s', '--start', action='store_const', const=True)
    parser.add_argument('-r', '--reload', action='store_const', const=True)
    parser.add_argument('-f', '--foreground', action='store_const', const=True)
    args = parser.parse_args()
    main(settings.LOG_FILE)
    if args.stop and args.start:
        print("Uhh. Something one maybe?")
        # Wrong arg
        exit(22)

    elif args.start:
        start_daemon()

    elif args.stop:
        stop_daemon()

    elif args.reload:
        stop_daemon()
        start_daemon()

    elif args.foreground:
        main(settings.LOG_FILE)
