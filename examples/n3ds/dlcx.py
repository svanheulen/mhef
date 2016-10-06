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
import base64

import mhef.n3ds


parser = argparse.ArgumentParser(description='Encrypts or decrypts a DLC file from MHX')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('region', choices=('JPN', 'USA', 'EUR'), help='game region')
parser.add_argument('key', help='DLC Blowfish key')
parser.add_argument('--pubkey', default=None, help='Dynamic DLC public key')
parser.add_argument('inputfile', help='DLC input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

if args.pubkey:
    args.pubkey = base64.b64decode(args.pubkey)

dc = mhef.n3ds.DLCXCipher(mhef.n3ds.MHX_JP, args.key, args.pubkey)
if args.region == 'USA':
    dc = mhef.n3ds.DLCXCipher(mhef.n3ds.MHX_NA, args.key, args.pubkey)
elif args.region == 'EUR':
    dc = mhef.n3ds.DLCXCipher(mhef.n3ds.MHX_EU, args.key, args.pubkey)

try:
    if args.mode == 'e':
        dc.encrypt_file(args.inputfile, args.outputfile)
    else:
        dc.decrypt_file(args.inputfile, args.outputfile)
except ValueError:
    print('Error: The file is corrupt, the Blowfish key is incorrect, or the public key is incorrect.')

