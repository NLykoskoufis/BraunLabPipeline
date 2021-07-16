#!/usr/bin/env python3 

import os
from os import path, access, system
from sys import stderr, argv
import smtplib
from email.mime.text import MIMEText



def writeEmail(addresses, subject, msg):
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
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, addresses, msg.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        stderr.write('Error, unable to send mail')

