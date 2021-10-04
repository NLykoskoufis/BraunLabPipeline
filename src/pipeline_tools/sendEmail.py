#!/usr/bin/env python3 

import argparse
from sys import argv
from writeEmail import writeEmail


parser = argparse.ArgumentParser(description='Call to write e-mail and log')
parser.add_argument('-msg', dest='msg', type=str, required=True, nargs=1, help='Message to send')


parser.add_argument('-subject', dest='subject', type=str, required=False, nargs=1, help='Subject for the email')
parser.add_argument('-add', dest='addresses', type=str, required=False, nargs='+', help='List of email addresses separate by space: i.e user@x.com user2@x.com')
parser.add_argument('-join', '--join-documents', dest='joinFile', type=str, required=False, help="Documents to be attached to mail .")
args = parser.parse_args()

if(args.addresses):
    writeEmail(args.addresses, args.subject[0], args.msg[0],args.joinFile)
