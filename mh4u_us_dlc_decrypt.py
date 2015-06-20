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

import array
import hashlib
import sys

from Crypto.Cipher import Blowfish


cipher = Blowfish.new(b'AgK2DYheaCjyHGPB')
data = array.array('I', open(sys.argv[1], 'rb').read())
data.byteswap()
size = data.pop()
data = array.array('I', cipher.decrypt(data.tobytes()))
data.byteswap()
data = data.tobytes()[:size]
sha1sum = data[-20:]
data = data[:-20]
open(sys.argv[2], 'wb').write(data)
if sha1sum == hashlib.sha1(data).digest():
    print('SHA1 is valid.')
else:
    print('SHA1 is invalid.')

