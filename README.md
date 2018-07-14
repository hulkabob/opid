# Orange PI GPIO Daemon. 

This is a python implementation of a daemon, which main purpose is 
to control certain GPIO pins. 
Like if you have your smarthouse system, but you want 
something really low-level and simplistic? Your pin is opening a 
transistor or doing other type of "intellectual" stuff? 

Well, you might be looking on the tool of choice. 

All communication is done via UNIX socket. The idea is to send commands
in some language. (Currently I'm looking also towards JSON's and YAML's 
as command containers.) Currently it's implemented via 
semantic language. Like "item - state". 
What's fancy about this, is flexible "semantics" maps. As we 
have boolean states of a GPIO pin, there are two groups of states. 
Suddenly, positive and negative. 



If you want to add something to it - feel free! 

License: MIT. 

Version: 0.88

### Todo: 
 * Todo todo
 * Todo 
 * Todo todo
 * todo tododododooooo dododododo
 
 ![Pink Panther ](./pink-panther.png)

 **Now seriously**: 
 * ~~Support for json / yaml bulk commands.~~
 * Setup script. 
 * Init / Unit file. 
 * Daemon interacting tool. (How to call it? opip? opii? opido?)
 * Comments on unobvious stuff and help messages. 
 
## Usage: 

You have several options: 
* interfacing it via socket
* using opip tool. (TBD)

### Socket: 

`socat - /run/opid/opid.pid`

#### opip tool

```
TBD
```

### Commands:


Notation: `<PIN/ALIAS>` `<STATE>`

Pin can be described in any of desired GPIO_MODES, 
if it was previously set in settings.
PIN/ALIAS is case sensitive!

State: `up/true/on` or `down/false/off`

```
PA14 On

PA13 down

Magic_Lamp off

Drawbridge Up
```
If Alias or pin is misspelled or unknown, deamon will respond with `Unkown command`
and close the socket connection. 
## Configs: 
By default, should be stored in /etc/opid/settings.py
But you're not limited to change location of the config file 
in opid.py:

`settings_location = "./settings.py"`

So you've got a number of things to configure. 
Firstly - how you will name your pins. 
In which mode you want it to operate? 

```GPIO_MODE = "SUNXI"```

Available GPIO modes are: `SUNXI`, `BCM`, `BOARD`.
For example, here is my own definition of used pins:
 
```
PINS = [
    "PA13", # Transistor got fried beause this dude works as TTL Tx on startup.
    "PA14", #
    "PD14", #
    "PC4",  #
]
```

Now the sweet part: you feel like screwed up remembering 
which pin is doin' what? We have aliases! A map between a pin and a 
some sort of definition of a device. For an example:   

```
# This is sort of alias tool. When you associate a pin with a device it's controlling. For logs exclusively.
ALIASES = {
    "PA13" : "Lamp",
    "PA14" : "Fan",
    "PD14" : "Relay",
    "PC7" : "Magic_lamp",
}
```
Some simple things like user, group, umask. (Doesn't change anything, 
as I didn;t implement this yet.)
```
#USER = "opid"
GROUP = "opid"
UMASK = 0o002

```

And run files location. 
```
#RUN_FILES = "/run/opid/"
RUN_FILES = "./opid_run/"
#PID_FILE = "/run/opid/opid.pid"
PID_FILE = "opid.pid"
#SOCKET = "/run/opid/pile.sock"
SOCKET = "./opid.sock"
```
