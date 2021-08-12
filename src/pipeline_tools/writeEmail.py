#!/usr/bin/env python3 

from email.mime.nonmultipart import MIMENonMultipart
import os
from os import path, access, system
from sys import stderr, argv
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders


def writeEmail(addresses, subject, body,attachments=None):
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
    msg = MIMEMultipart()
    #msg = MIMEText(msg);
    msg['Subject'] = subject
    msg['From'] = sender 
    msg['To'] = ", ".join(addresses)
    
    # Add body to email 
    msg.attach(MIMEText(body, "plain"))
    
    
    #if attachments != None: 
    filename = "/srv/beegfs/scratch/users/l/lykoskou/Braun_lab/ATAC/test2/pipeline_report.zip"  # In same directory as script

    # Open filename file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        "attachment; filename= pipeline_report.zip",
    )

    # Add attachment to message and convert message to string
    msg.attach(part)
    
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, addresses, msg.as_string())
        smtpObj.quit()
    except smtplib.SMTPException:
        stderr.write('Error, unable to send mail')

