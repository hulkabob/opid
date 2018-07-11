#!/usr/bin/env python3
import os
#import OPi.GPIO as GPIO
import socket
import signal
import daemon
import lockfile
import importlib.util
import settings
from syslog import syslog, LOG_CRIT, LOG_ERR, LOG_INFO
import sys
"""
Error codes:
22 - Misconfigured. Invalid arguments and stuff.

"""

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
"""
positive_state = ["on", "true", "up"]
negative_state = ["off", "false", "down"]
######## Importing settings ###################

spec = importlib.util.spec_from_file_location("settings", "./settings.py")
foo = importlib.util.module_from_spec(spec)

######## Defining a socket ####################
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
###############################################
def init():
    """
    Create dir at settings.RUN_FILES
    Binds a socket to settings.SOCKET addr
    and starts to listen it.

    Also sets all pins specified in settings.PINS to output mode.

    :return:
    """
    global sock

    if os.path.isdir(settings.RUN_FILES):
        pass
    else:
        os.makedirs(settings.RUN_FILES)

    if settings.GPIO_MODE == "SUNXI":
        GPIO.setmode(GPIO.SUNXI)

    elif settings.GPIO_MODE == "BCM":
        GPIO.setmode(GPIO.BCM)

    elif settings.GPIO_MODE == "BOARD":
        GPIO.setmode(GPIO.BOARD)

    else:
        syslog(LOG_CRIT, "Unknown GPIO_MODE specified!")
        print("Unknown GPIO_MODE specified!",  file=sys.stderr)
        exit(22) #define EINVAL 22 /* Invalid argument */



    for pin in settings.PINS:
        GPIO.setup(pin, GPIO.OUT)

    try:
        sock.bind(settings.SOCKET)
        sock.listen(1)
    except socket.error as msg:
        sock.close()
        print(msg)
        sock = None
        exit(msg.errno)

    return


def main():

        global sock
        syslog('Started OPID Daemon')

        while True:
            # Wait for a connection

            syslog('Waiting for connection')
            connection, client_address = sock.accept()
            try:
                # Receive the data in chunks and parse it.
                while True:
                    """
                    Notation: <PIN/ALIAS> <STATE>
                    Pin can be described in any of desired GPIO_MODES? if it was previously set in settings.
                    PIN/ALIAS is case sensitive!
                     
                    State: up/true/on or down/false/off
                    
                    """
                    data = connection.recv(256).decode("utf-8").rstrip()
                    rez = data.split(" ")

                    if len(rez) == 1: # If we have only "\n"
                        break

                    data = list(filter(None, rez)) # fastest
                    thing_to_control = data[0]
                    command = data[1].lower()

                    if thing_to_control in settings.PINS:

                        if command in positive_state:
                            GPIO.output(thing_to_control, True)

                        if command in negative_state:
                            GPIO.output(thing_to_control, False)

                        connection.sendall(b"Success\n")


                    elif thing_to_control in settings.ALIASES.values():

                        verified_pin = None
                        for pin, alias in settings.ALIASES.items():
                            if thing_to_control == alias:
                                verified_pin = pin

                        if verified_pin == None:
                            syslog(LOG_ERR, 'Unknown alias/pin name')
                            connection.sendall(b"\nUnrecognized command\nUnknown alias/pin name\n")
                            break


                        if command in positive_state:
                            GPIO.output(verified_pin, True)

                        if command in negative_state:
                            GPIO.output(verified_pin, False)

                        connection.sendall(b"Success\n")


                    else:
                        syslog(LOG_INFO, 'no data from socket')
                        print(thing_to_control)
                        connection.sendall(b"\nUnrecognized command\n")
                        break

            finally:
                # Clean up the connection
                print("Closing conn")
                connection.close()




def cleanup():
    os.remove(settings.PID_FILE)
    os.remove(settings.SOCKET)
    os.rmdir(settings.RUN_FILES)
    return


def reload_config():
    # TODO: Find how to recreate central context.
    return


if __name__ == "__main__":
    context = daemon.DaemonContext(
        working_directory=settings.RUN_FILES,
        umask=settings.UMASK,
        pidfile=lockfile.FileLock(settings.PID_FILE),
    )

    context.signal_map = {
        signal.SIGTERM: cleanup,
        signal.SIGHUP: 'terminate',
        signal.SIGUSR1: reload_config,
    }
    init()
    main()
