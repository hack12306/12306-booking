#!/usr/bin/python

# encoding: utf8

import re
import sys

from booking.command import booking

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(booking())