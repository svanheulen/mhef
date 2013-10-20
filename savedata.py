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
parser.add_argument('game', choices=['3rd', '2ndg_jp', '2ndg_na', '2ndg_eu', '2nd_jp', '2nd_na', '2nd_eu'], help='version of Monster Hunter')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('inputfile', help='savedata input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()


if args.game == '3rd':
    from mhef.mhp3rd import *
elif args.game.startswith('2ndg'):
    from mhef.mhp2ndg import *
else:
    from mhef.mhp2nd import *

psc = None
if args.game.endswith('_jp') or args.game == '3rd':
    psc = mhef.PSPSavedataCipher(PSPSAVEDATA_KEY_JP)
elif args.game.endswith('_na'):
    psc = mhef.PSPSavedataCipher(PSPSAVEDATA_KEY_NA)
elif args.game.endswith('_eu'):
    psc = mhef.PSPSavedataCipher(PSPSAVEDATA_KEY_EU)

temp = None
if args.mode == 'e':
    temp = psc.encrypt(open(args.inputfile, 'rb').read())
else:
    temp = psc.decrypt(open(args.inputfile, 'rb').read())

if args.game.startswith('2nd_'):
    open(outputfile, 'wb').write(temp)
else:
    sc = None
    if args.game.endswith('_jp') or args.game == '3rd':
        sc = mhef.SavedataCipher(SAVEDATA_KEY_JP)
    elif args.game.endswith('_na'):
        sc = mhef.SavedataCipher(SAVEDATA_KEY_NA)
    elif args.game.endswith('_eu'):
        sc = mhef.SavedataCipher(SAVEDATA_KEY_EU)
    if args.mode == 'e':
        open(args.outputfile, 'wb').write(sc.encrypt(temp))
    else:
        open(args.outputfile, 'wb').write(sc.decrypt(temp))

