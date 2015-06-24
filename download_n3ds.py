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
import urllib.request


parser = argparse.ArgumentParser(description='Downloads a file from the Monster Hunter 4 Ultimate DLC website')
parser.add_argument('remotefile', help='remote file to download')
parser.add_argument('outputfile', help='output file')
args = parser.parse_args()

uri = 'http://goshawk.capcom.co.jp/3ds/mh4g_us_/{}'.format(args.remotefile)
headers = {'User-Agent': 'Capcom Browser Services for MonsterHunter_4G'}

request = urllib.request.Request(uri, headers=headers)
response = urllib.request.urlopen(request)
open(args.outputfile, 'wb').write(response.read())

