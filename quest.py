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


parser = argparse.ArgumentParser(description='Encrypts or decrypts a quest file from Monster Hunter 3rd or 2nd G')
parser.add_argument('game', choices=['3rd', '2ndg_jp', '2ndg_na', '2ndg_eu'], help='version of Monster Hunter')
parser.add_argument('mode', choices=['e', 'd'], help='(e)ncrypt or (d)ecrypt')
parser.add_argument('inputfile', help='quest input file')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

if args.game == '3rd':
    from mhef.mhp3rd import *
else:
    from mhef.mhp2ndg import *

qc = None
if args.game.endswith('_na'):
    qc = mhef.QuestCipher(QUEST_KEY_DEFAULT, QUEST_KEY_MODIFIER, QUEST_HASH_SALT_NA)
elif args.game.endswith('_eu'):
    qc = mhef.QuestCipher(QUEST_KEY_DEFAULT, QUEST_KEY_MODIFIER, QUEST_HASH_SALT_EU)
else:
    qc = mhef.QuestCipher(QUEST_KEY_DEFAULT, QUEST_KEY_MODIFIER, QUEST_HASH_SALT_JP)

if args.mode == 'e':
    qc.encrypt_file(args.inputfile, args.outputfile)
else:
    qc.decrypt_file(args.inputfile, args.outputfile)

