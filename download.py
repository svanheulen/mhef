#!/usr/bin/python2.7

# Copyright 2012 Seth VanHeulen
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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import urllib2

parser = argparse.ArgumentParser(description='downloads a page or file from the MHP3rd event quest website (hint: the index page is DL_TOP.PHP and you can find the other pages/files from there)')
parser.add_argument('remotepath', help='remote file to download')
parser.add_argument('output', type=argparse.FileType('wb'), help='local output file')
args = parser.parse_args()

uri = 'http://crusader.capcom.co.jp/psp/MHP3rd/'
headers = {'User-Agent': 'Capcom Portable Browser v1.4 for MonsterHunterPortable3rd',
           'Referer': uri + 'DL_MENU.PHP'}

request = urllib2.Request(uri + args.remotepath, '', headers)
response = urllib2.urlopen(request)
args.output.write(response.read())
args.output.close()
