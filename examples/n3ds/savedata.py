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


parser = argparse.ArgumentParser(description='Encrypts or decrypts a savedata file from Monster Hunter 4 Ultimate')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('inputfile', help='savedata input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

sc = mhef.n3ds.SavedataCipher(mhef.n3ds.MH4G_NA)

if args.mode == 'e':
    sc.encrypt_file(args.inputfile, args.outputfile)
else:
    sc.decrypt_file(args.inputfile, args.outputfile)

