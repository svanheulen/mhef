#!/usr/bin/python

# Copyright 2013-2015 Seth VanHeulen
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

from __future__ import print_function
import argparse
import binascii

import mhef.psp


parser = argparse.ArgumentParser(description='Encrypts or decrypts a savedata file from Monster Hunter')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('game', choices=['3', '2G_JP', '2G_NA', '2G_EU', '2_JP', '2_NA', '2_EU', '1_JP', '1_NA', '1_EU'], help='version of Monster Hunter')
parser.add_argument('inputfile', help='savedata input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

game = mhef.psp.MHP3_JP
if args.game == '1_JP':
    game = mhef.psp.MHP_JP
elif args.game == '1_NA':
    game = mhef.psp.MHP_NA
elif args.game == '1_EU':
    game = mhef.psp.MHP_EU
elif args.game == '2G_JP':
    game = mhef.psp.MHP2G_JP
elif args.game == '2G_NA':
    game = mhef.psp.MHP2G_NA
elif args.game == '2G_EU':
    game = mhef.psp.MHP2G_EU
elif args.game == '2_JP':
    game = mhef.psp.MHP2_JP
elif args.game == '2_NA':
    game = mhef.psp.MHP2_NA
elif args.game == '2_EU':
    game = mhef.psp.MHP2_EU

temp = open(args.inputfile, 'rb').read()
psc = mhef.psp.PSPSavedataCipher(game)
if args.mode == 'd':
    print('hash:', binascii.hexlify(psc.hash(temp)).decode())
    temp = psc.decrypt(temp)

if game >= mhef.psp.MHP2G_JP:
    sc = mhef.psp.SavedataCipher(game)
    if args.mode == 'e':
        temp = sc.encrypt(temp)
    else:
        temp = sc.decrypt(temp)

if args.mode == 'e':
    temp = psc.encrypt(temp)
    print('hash:', binascii.hexlify(psc.hash(temp)).decode())

open(args.outputfile, 'wb').write(temp)

