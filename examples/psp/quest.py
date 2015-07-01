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

import mhef.psp


parser = argparse.ArgumentParser(description='Encrypts or decrypts a quest file from Monster Hunter 3rd or 2nd G')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('game', choices=['3', '2G_JP', '2G_NA', '2G_EU'], help='version of Monster Hunter')
parser.add_argument('inputfile', help='quest input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

game = mhef.psp.MHP3_JP
if args.game == '2G_JP':
    game = mhef.psp.MHP2G_JP
elif args.game == '2G_NA' or args.game == '2G_EU':
    game = mhef.psp.MHP2G_NA

qc = mhef.psp.QuestCipher(game)

if args.mode == 'e':
    csum = qc.encrypt_file(args.inputfile, args.outputfile)
else:
    csum = qc.decrypt_file(args.inputfile, args.outputfile)
print('csum:', csum)

