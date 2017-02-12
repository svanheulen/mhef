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
try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen


parser = argparse.ArgumentParser(description='Downloads a file from the Monster Hunter 4 Ultimate DLC website')
parser.add_argument('game', choices=('4G', 'X', 'SS'), help='game version')
parser.add_argument('region', choices=('JPN', 'USA', 'EUR', 'KOR', 'TWN'), help='game region')
parser.add_argument('remotefile', help='remote file to download')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

uri = 'http://goshawk.capcom.co.jp/3ds/mh4g_nihon/{}'.format(args.remotefile)
headers = {'User-Agent': 'Capcom Browser Services for MonsterHunter_4G'}
if args.game == '4G':
    if args.region == 'USA':
        uri = 'http://goshawk.capcom.co.jp/3ds/mh4g_us_/{}'.format(args.remotefile)
    elif args.region == 'EUR':
        uri = 'http://goshawk.capcom.co.jp/3ds/mh4g_eu_/{}'.format(args.remotefile)
    elif args.region == 'KOR':
        uri = 'http://goshawk.capcom.co.jp/3ds/mh4g_kr_/{}'.format(args.remotefile)
    elif args.region == 'TWN':
        uri = 'http://goshawk4g.capcom.co.jp/redgiant/dl/pro_tw/{}'.format(args.remotefile)
elif args.game == 'X':
    uri = 'http://spector.capcom.co.jp/3ds/mhx_new_jp/{}'.format(args.remotefile)
    headers = {'User-Agent': 'Capcom Browser Services for MonsterHunter_X'}
    if args.region == 'USA':
        uri = 'http://spector.capcom.co.jp/3ds/mhx_us/{}'.format(args.remotefile)
    elif args.region == 'EUR':
        uri = 'http://spector.capcom.co.jp/3ds/mhx_eu/{}'.format(args.remotefile)
elif args.game == 'SS':
    uri = 'http://voodoo.capcom.co.jp/3ds/mhss_jp/{}'.format(args.remotefile)
    headers = {'User-Agent': 'Capcom Browser Services for MonsterHunter_SS'}

request = Request(uri, headers=headers)
response = urlopen(request)
open(args.outputfile, 'wb').write(response.read())

