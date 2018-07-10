import os
import OPi.GPIO as GPIO
import socket
import signal
import daemon
import lockfile
import importlib.util
import settings
import syslog
import sys

"""
Error codes:
22 - Misconfigured. Invalid arguments and stuff.

"""

positive_state = ["on", "true", "up"]
negative_state = ["off", "false", "down"]
######## Importing settings ###################

spec = importlib.util.spec_from_file_location("settings", "/etc/opid/settings.py")
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

    if os.path.isdir(settings.RUN_FILES):
        pass
    else:
        os.makedirs(settings.RUN_FILES)

    if settings.GPIO_MODE == "SUNXI":
        GPIO.setmode(GPIO.SUNXI)

    elif settings.GPIO_MODE == "BCM":
        pass

    elif settings.GPIO_MODE == "wpi":
        pass

    else:
        syslog.syslog(syslog.LOG_CRIT, "Unknown GPIO_MODE specified!")
        print("Unknown GPIO_MODE specified!",  file=sys.stderr)
        exit(22) #define EINVAL 22 /* Invalid argument */



    for pin in settings.PINS:
        GPIO.setup(pin, GPIO.OUT)

    sock.bind(settings.SOCKET)
    sock.listen(1)
    return


def main():

    while True:
        # Wait for a connection

        syslog.syslog('Waiting for connection')
        connection, client_address = sock.accept()
        try:
            # Receive the data in chunks and parse it.
            while True:
                """
                Notation: <PIN/ALIAS> <STATE>
                Pin can be described in any of desired GPIO_MODES? if it was previous;y set in settings. 
                State: up/true/on or down/false/off
                
                """
                data = connection.recv(256)
                data = data.split(" ")
                data = filter(None, data)  # fastest

                if data[0] in settings.PINS:
                    pass
                elif data in settings.PINS.values():


                else:
                    print('no data from', client_address)
                    connection.sendall("Unrecognized command")
                    break

        finally:
            # Clean up the connection
            connection.close()


def cleanup():
    return


def reload_config():
    # TODO: Find how to recreate central context.
    return


context = daemon.DaemonContext(
    working_directory = settings.RUN_FILES,
    umask = settings.UMASK,
    pidfile = lockfile.FileLock(settings.PID_FILE),
    )

context.signal_map = {
    signal.SIGTERM: cleanup,
    signal.SIGHUP: 'terminate',
    signal.SIGUSR1: reload_config,
    }


init()

with context:
    main()