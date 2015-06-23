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

from Crypto.Cipher import Blowfish


MH3G_JP = 0
MH3G_NA = 1
MH3G_EU = 2
MH4_JP = 3
MH4_NA = 4
MH4_EU = 5
MH4G_JP = 6
MH4G_NA = 7
MH4G_EU = 8


class DLCCipher:
    _mh4g_na_key = b'AgK2DYheaCjyHGPB'

    def __init__(self, game):
        if game == MH4G_NA:
            self._cipher = Blowfish.new(self._mh4g_na_key)
        else:
            raise ValueError('Ivalid game selected.')

    def encrypt(self, buff):
        buff += hashlib.sha1(buff).digest()
        size = len(buff)
        if len(buff) % 8 != 0:
            buff += b'\x00' * (8 - len(buff) % 8)
        buff = array.array('I', buff)
        buff.byteswap()
        buff = array.array('I', self._cipher.encrypt(buff.tobytes()))
        buff.append(size)
        buff.byteswap()
        return buff.tobytes()

    def decrypt(self, buff):
        buff = array.array('I', buff)
        buff.byteswap()
        size = buff.pop()
        if size > len(buff) * 4:
            raise ValueError('Invalid file size in footer.')
        buff = array.array('I', self._cipher.decrypt(buff.tobytes()))
        buff.byteswap()
        buff = buff.tobytes()[:size]
        md = buff[-20:]
        buff = buff[:-20]
        if md != hashlib.sha1(buff).digest():
            raise ValueError('Invalid SHA1 hash in footer.')
        return buff

    def encrypt_file(self, dlc_file, out_file):
        with open(dlc_file, 'rb') as dlc, open(out_file, 'wb') as out:
            out.write(self.encrypt(dlc.read()))

    def decrypt_file(self, dlc_file, out_file):
        with open(dlc_file, 'rb') as dlc, open(out_file, 'wb') as out:
            out.write(self.decrypt(dlc.read()))

