#!/usr/bin/python

# Copyright 2015 Seth VanHeulen
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

import mhef.n3ds


parser = argparse.ArgumentParser(description='Encrypts or decrypts a DLC file from MH4U')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('region', choices=('JPN', 'USA', 'EUR', 'KOR', 'TWN'), help='game region')
parser.add_argument('inputfile', help='DLC input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

dc = mhef.n3ds.DLCCipher(mhef.n3ds.MH4G_JP)
if args.region == 'USA':
    dc = mhef.n3ds.DLCCipher(mhef.n3ds.MH4G_NA)
elif args.region == 'EUR':
    dc = mhef.n3ds.DLCCipher(mhef.n3ds.MH4G_EU)
elif args.region == 'KOR':
    dc = mhef.n3ds.DLCCipher(mhef.n3ds.MH4G_KR)
elif args.region == 'TWN':
    dc = mhef.n3ds.DLCCipher(mhef.n3ds.MH4G_TW)

try:
    if args.mode == 'e':
        dc.encrypt_file(args.inputfile, args.outputfile)
    else:
        dc.decrypt_file(args.inputfile, args.outputfile)
except ValueError:
    print('Error: The file is corrupt, or you selected the wrong region.')

