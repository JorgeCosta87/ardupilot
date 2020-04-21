#!/usr/bin/env python

import sys
from PointValidation import EvaluateMission

if len(sys.argv) < 3:
    print 'usage: ' + sys.argv[0] + ' <mission> < run >'
    print 'Example: ' + sys.argv[0] + 'mymissionfile.txt myrunattempt.log'

print EvaluateMission(sys.argv[1], sys.argv[2]).name