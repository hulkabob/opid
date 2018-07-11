# Orange PI GPIO Daemon. 

This is a python implementation of a daemon, which main purpose is 
to control certain GPIO pins. 
Like if you have your smarthouse system, but you want 
something really low-level and simplistic? Your pin is opening a 
transistor or doing other type of "intellectual" stuff? 

Well, you might be looking on the tool of choice. 

All communication is done via UNIX socket. The idea is to send commands
in some language. (Currently I'm looking towards JSON's and YAML's 
as command containers.) It also can be a specialized protocol, 
with fields and stuff, but not for now. 

If you ant to add something to it - feel free! 

License: MIT. 

Version: 0.2 

Configs: 
TBD

 


