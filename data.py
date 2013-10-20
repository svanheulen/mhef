#!/usr/bin/python3

# Copyright 2013 Seth VanHeulen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse

import mhef


parser = argparse.ArgumentParser(description='Encrypts or decrypts the DATA.BIN file from Monster Hunter 3rd or 2nd G')
parser.add_argument('game', choices=['3rd', '2ndg'], help='version of Monster Hunter')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('inputfile', help='DATA.BIN input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

if args.game == '3rd':
    from mhef.mhp3rd import *
else:
    from mhef.mhp2ndg import *

dc = mhef.DataCipher()

if args.mode == 'e':
    dc.encrypt_file(args.inputfile, args.outputfile, DATA_EXCEPTIONS)
else:
    dc.decrypt_file(args.inputfile, args.outputfile, DATA_EXCEPTIONS)

