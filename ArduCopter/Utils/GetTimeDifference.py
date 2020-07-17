#!/usr/bin/env python

from datetime import datetime
from sys import argv

if len(argv) != 3:
    print "2 arguments required!\n"
    exit(1)

dateA = datetime.strptime(argv[1], '%Y-%m-%d %H:%M:%S.%f')
dateB = datetime.strptime(argv[2], '%Y-%m-%d %H:%M:%S.%f')

if dateA > dateB:
    difference = dateA - dateB
else:
    difference = dateB - dateA

print difference