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
GROUP = "opid"

UMASK = 0o002

GPIO_MODE = "SUNXI"
#RUN_FILES = "/run/opid/"
RUN_FILES = "./opid_run/"
#PID_FILE = "/run/opid/opid.pid"
PID_FILE = "./opid_run/opid.pid"
#SOCKET = "/run/opid/pile.sock"
SOCKET = "./opid_run/opid.sock"

