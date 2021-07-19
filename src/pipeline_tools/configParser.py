#!/usr/bin/env python3 

from sys import argv
import json



def getConfigDict(configFilePath):
    f = open(configFilePath, "rt")
    configDict = {}
    for line in f: 
        if line.startswith("#") or not line.strip(): 
            continue 
        else:
            configList = (line.rstrip()).split(",")
            configDict[configList[0]] = " ".join(configList[1:]) # The first value is the key name and the value is all the rest. Here you can add the specific commands to use etc. 
    f.close()
    return configDict


def dict2File(dict,outputFile):
    f = open(outputFile, "w")
    f.write(json.dumps(dict))