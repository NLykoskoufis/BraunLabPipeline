#!/usr/bin/env python3 

import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[93m'
    WARNING = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class verbose:
    def __init__(self): 
        pass

    
    def ctitle(s):
        print(bcolors.HEADER,bcolors.BOLD,end='')
        print(s)
        print(bcolors.ENDC,end='')
        
    def title(s): 
        print(bcolors.OKBLUE,bcolors.BOLD,end='')
        print(s)
        print(bcolors.ENDC,end='')
        
    def bullet(s):
        print("  * ", end='')
        print(s)
    
    def warning(s):
        print(bcolors.WARNING,end='')
        print(s)
        print(bcolors.ENDC,end='')
    
    def error(s):
        print(bcolors.FAIL,bcolors.BOLD,end='')
        print(s)
        print(bcolors.ENDC,end='')
        sys.exit(1)
    
    def done(s):
        print(bcolors.OKGREEN,end='')
        print(s)
        print(bcolors.ENDC,end='')
    

        
        
        