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
    - Loading and translating jsons
    - Loading and translating YAMLs. 
    - Doing all the stuff not looking at the socket command type. (Semantic, JSON and YAML respectively)
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
        '''))
    parser.add_argument('-m', '--mode', help="Command mode. semantic, yaml and json are supported.")
    parser.add_argument('-f', '--file', help="When yaml or json are seletcted, point to the json or yaml file. "
                                             "If not specified, stdin will serve as file source.")
    parser.add_argument('-p', '--pin', help="When semantic mode is selected, give the pin / alias which to set")
    parser.add_argument('-s', '--state', help="And give the desired pin state. On/Off, Up/Down, True/False are "
                                              "appropriate by default.")
    args = parser.parse_args()