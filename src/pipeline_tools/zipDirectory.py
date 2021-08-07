#!/usr/bin/env python3 
import zipfile 
import os 
from sys import argv

def zipDir(dirpath, outFullName):
    '''
         Compress the specified folder
         :param dirpath: target folder path
         :param outFullName: compressed file save path +XXXX.zip
         :return: none
    '''
    zip = zipfile.ZipFile(outFullName, 'w', zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        #Remove the target and path, only compress the files and folders under the target folder
        fpath = path.replace(dirpath,'')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath,filename))
    zip.close()
    
if __name__ == "__main__":
    zipDir(*argv[1:])
    
