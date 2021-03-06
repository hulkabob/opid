PINS = [
    "PA13", # Transistor got fried beause this dude works as TTL Tx on startup.
    "PA14", #
    "PD14", #
    "PC4",  #
]

# This is sort of alias tool. When you associate a pin with a device it's controlling. For logs exclusively.
ALIASES = {
    "PA13" : "Lamp",
    "PA14" : "Fan",
    "PD14" : "Relay",
    "PC7" : "Magnet_Lock",
}


#USER = "opid"
#GROUP = "opid"
GROUP = "masterbob"

UMASK = 0o017 # Security!

COMMAND_FORMAT = "JSON"
"""
Allowd are "SEMANTIC", "JSON" and "YAML"
"""

GPIO_MODE = "SUNXI"
#RUN_FILES = "/run/opid/"
RUN_FILES = "./opid_run/"
#PID_FILE = "/run/opid/opid.pid"
PID_FILE = "opid.pid"
#SOCKET = "/run/opid/pile.sock"
SOCKET = "./opid.sock"
LOG_FILE = "./opid.log"

