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


parser = argparse.ArgumentParser(description='Encrypts or decrypts a savedata file from Monster Hunter 3rd, 2nd G or 2nd')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('game', choices=['3', '2G_JP', '2G_NA', '2G_EU', '2_JP', '2_NA', '2_EU'], help='version of Monster Hunter')
parser.add_argument('inputfile', help='savedata input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

game = mhef.MHP3_JP
if args.game == '2G_JP':
    game = mhef.MHP2G_JP
elif args.game == '2G_NA':
    game = mhef.MHP2G_NA
elif args.game == '2G_EU':
    game = mhef.MHP2G_EU
elif args.game == '2_JP':
    game = mhef.MHP2_JP
elif args.game == '2_NA':
    game = mhef.MHP2_NA
elif args.game == '2_EU':
    game = mhef.MHP2_EU

temp = open(args.inputfile, 'rb').read()
psc = mhef.PSPSavedataCipher(game)
if args.mode == 'd':
    temp = psc.decrypt(temp)

if game >= mhef.MHP2G_JP:
    sc = mhef.SavedataCipher(game)
    if args.mode == 'e':
        temp = sc.encrypt(temp)
    else:
        temp = sc.decrypt(temp)

if args.mode == 'e':
    temp = psc.encrypt(temp)

open(args.outputfile, 'wb').write(temp)

