#!/usr/bin/env python3 

import os
from os import path, access, system
from sys import stderr, argv
import smtplib
from email.mime.text import MIMEText
import zipfile 

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

def writeEmail(addresses, subject, msg,attachments=None):
    """[send email]

    Args:
        addresses ([list]): [email address to send mail]
        subject ([str]): [Subject of the mail]
        msg ([str]): [message to be sent]
    """    
    if isinstance(addresses, str):
        stderr.write("Argument addresses=" + addresses + " passed to writeEmail is not a list\n")
        return -1
    sender =  'nikolaos.lykoskoufis@unige.ch'
    msg = MIMEText(msg);
    msg['Subject'] = subject
    msg['From'] = sender 
    msg['To'] = ", ".join(addresses)
    
    if attachments != None: 
        

    
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, addresses, msg.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        stderr.write('Error, unable to send mail')

