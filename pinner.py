#!/bin/env python3
import argparse
import importlib.util
import json
import os
import socket
import sys
import textwrap
import signal
import yaml

"""
            d8,                                   
           `8P                                    
                                                  
?88,.d88b,  88b 88bd88b   88bd88b  d8888b  88bd88b
`?88'  ?88  88P 88P' ?8b  88P' ?8bd8b_,dP  88P'  `
  88b  d8P d88 d88   88P d88   88P88b     d88     
  888888P'd88'd88'   88bd88'   88b`?888P'd88'     
  88P'                                            
 d88                                              
 ?8P                                              

Purpose: interact with GPIO daemon - OPID.
Planned features: 
    - Support for semantics - pin-state commands (argparse)
    - Loading jsons
    - Loading YAMLs. 
"""
########################## Loading settings #################################
settings_location = "./settings.py"
spec = importlib.util.spec_from_file_location("settings", settings_location)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sys.modules["settings"] = module
try:
    import settings
except ImportError:
    print("[!] No settings in {location}".format(location=settings_location))
    exit(2)
#############################################################################


def send_to_socet(conn_socket, command_package):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    sock.connect(conn_socket)
    sock.sendall(command_package)


def read_file(file):
    command_package = ""
    file_desc = open(file, "r")
    for line in file_desc:
        command_package += line
    file_desc.close()
    return command_package


def check_type(file):
    try:
        json.loads(file)
        return "JSON"
    except ValueError:
        is_json = False

    try:
        yaml.safe_load(file)
        return "YAML"
    except yaml.YAMLError:
        is_yaml = False

    if not is_json and not is_yaml:
        return None


def translate_commands(command_package, type):
    semantic_format = "{pin} {state}"
    output_type = settings.COMMAND_FORMAT
    if type == output_type:
        return command_package
    else:
        if type == "YAML":
            commands = yaml.load(command_package)

        elif type == "JSON":
            commands = json.loads(command_package)

        elif type == "SEMANTIC":
            command_line = command_package.rstrip()
            command = command_line.split(" ")
            pin = command[0]
            state = command[1]
            commands = {
                'devices':[
                    {'pin':pin,
                     'state': state}
                ]
            }
    if output_type == "YAML":
        return yaml.dump(commands)

    elif output_type == "JSON":
        return json.dumps(commands)

    elif output_type == "SEMANTIC":
        commands_serialized = []
        for command in commands['devices']:
            commands_serialized.append(semantic_format.format(pin=command['pin'], state=command['state']))
        return commands_serialized



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='opid', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''
                d8,                                   
               `8P                                    
                                                      
    ?88,.d88b,  88b 88bd88b   88bd88b  d8888b  88bd88b
    `?88'  ?88  88P 88P' ?8b  88P' ?8bd8b_,dP  88P'  `
      88b  d8P d88 d88   88P d88   88P88b     d88     
      888888P'd88'd88'   88bd88'   88b`?888P'd88'     
      88P'                                            
     d88                                              
     ?8P                                              

        For Pinning tools.
        '''),
    epilog ="""
    Examples: 
        pinner -m semantic -p PA14 -s False
        pinner -p Magic_Lamp -s On
        pinner -m yaml -f ~/ps4_off.yaml
    
    """)
    parser.add_argument('-m', '--mode', default="semantic", help="Command mode. semantic, yaml and json are supported.")
    parser.add_argument('-f', '--file', help="When yaml or json are seletcted, point to the json or yaml file. "
                                             "If not specified, stdin will serve as file source.")
    parser.add_argument('-p', '--pin', help="When semantic mode is selected, give the pin / alias which to set")
    parser.add_argument('-s', '--state', help="And give the desired pin state. On/Off, Up/Down, True/False are "
                                              "appropriate by default.")
    args = parser.parse_args()

    if args.mode == "json" or args.mode == "yaml":
        command_package = read_file(args.file)
        file_type = check_type(command_package)
        commands = translate_commands(command_package, file_type)
        if type(commands) is list:
            for item in commands:
                send_to_socet(settings.SOCKET, item)
        else:
            send_to_socet(settings.SOCKET, commands)

    elif args.mode == "semantic":
        semantic_format = "{pin} {state}"
        command_package = semantic_format.format(pin=args.pin, state=args.state)
        commands = translate_commands(command_package, "SEMANTIC")
        send_to_socet(settings.SOCKET, commands)