#!/usr/bin/python

# Copyright 2012-2015 Seth VanHeulen
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
try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen


parser = argparse.ArgumentParser(description='Downloads a file from the Monster Hunter DLC websites (hint: the index page is DL_TOP.PHP)')
parser.add_argument('game', choices=['3', '2G_JP', '2G_NA', '2G_EU', '2_JP', '2_NA', '2_EU', '1'], help='version of Monster Hunter')
parser.add_argument('remotefile', help='remote file to download')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

uri = 'http://crusader.capcom.co.jp/psp/MHP3rd/'
headers = {'User-Agent': 'Capcom Portable Browser v1.4 for MonsterHunterPortable3rd'}
if args.game == '2G_JP':
    uri = 'http://viper.capcom.co.jp/psp/MHP2G/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.3 for MH_Portable_2nd_G'}
elif args.game == '2G_NA':
    uri = 'http://viper.capcom.co.jp/psp/MHP2GUSA/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.3 for MH_Portable_2nd_G'}
elif args.game == '2G_EU':
    uri = 'http://viper.capcom.co.jp/psp/MHP2GPAL/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.3 for MH_Portable_2nd_G'}
elif args.game == '2_JP':
    uri = 'http://skyhawk.capcom.co.jp/psp/MHP2/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.2 for MH2nd_Portable'}
elif args.game == '2_NA':
    uri = 'http://skyhawk.capcom.co.jp/psp/MHP2USA/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.2 for MH2nd_Portable'}
elif args.game == '2_EU':
    uri = 'http://skyhawk.capcom.co.jp/psp/MHP2PAL/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.2 for MH2nd_Portable'}
elif args.game == '1':
    uri = 'http://corsair.capcom.co.jp/psp/MHPSP/'
    headers = {'User-Agent': 'Capcom Portable Browser v1.0 for MH_Portable'}

if args.remotefile.startswith('QUEST/'):
    headers['Referer'] = uri + 'DL_MENU.PHP'
elif args.remotefile.startswith('OTOMO/'):
    headers['Referer'] = uri + 'DL_OTOMO.PHP'
elif args.remotefile.startswith('BONUS/'):
    headers['Referer'] = uri + 'DL_BONUS.PHP'
elif args.remotefile.startswith('NOSSL/QUEST/'):
    headers['Referer'] = uri + 'NOSSL/DL_MENU1.HTM'

request = Request(uri + args.remotefile, b'', headers)
response = urlopen(request)
open(args.outputfile, 'wb').write(response.read())

