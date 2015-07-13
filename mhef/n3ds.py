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
import random

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
MH4G_KR = 9


class SavedataCipher:
    def __init__(self, game):
        if game in (MH4G_JP, MH4G_NA, MH4G_EU):
            self._cipher = Blowfish.new(b'blowfish key iorajegqmrna4itjeangmb agmwgtobjteowhv9mope')
        else:
            raise ValueError('Ivalid game selected.')

    def _xor(self, buff, key):
        buff = array.array('H', buff)
        for i in range(len(buff)):
            if key == 0:
                key = 1
            key = key * 0xb0 % 0xff53
            buff[i] ^= key
        return buff.tostring()

    def encrypt(self, buff):
        csum = sum(bytearray(buff)) & 0xffffffff
        buff = array.array('I', buff)
        buff.insert(0, csum)
        seed = random.getrandbits(16)
        buff = array.array('I', self._xor(buff.tostring(), seed))
        buff.insert(0, (seed << 16) + 0x10)
        buff.byteswap()
        buff = array.array('I', self._cipher.encrypt(buff.tostring()))
        buff.byteswap()
        return buff.tostring()

    def decrypt(self, buff):
        buff = array.array('I', buff)
        buff.byteswap()
        buff = array.array('I', self._cipher.decrypt(buff.tostring()))
        buff.byteswap()
        seed = buff.pop(0) >> 16
        buff = array.array('I', self._xor(buff.tostring(), seed))
        csum = buff.pop(0)
        buff = buff.tostring()
        if csum != (sum(bytearray(buff)) & 0xffffffff):
            raise ValueError('Invalid checksum in header.')
        return buff

    def encrypt_file(self, savedata_file, out_file):
        savedata = open(savedata_file, 'rb').read()
        savedata = self.encrypt(savedata)
        open(out_file, 'wb').write(savedata)

    def decrypt_file(self, savedata_file, out_file):
        savedata = open(savedata_file, 'rb').read()
        savedata = self.decrypt(savedata)
        open(out_file, 'wb').write(savedata)


class DLCCipher:
    def __init__(self, game):
        if game == MH4G_NA or game == MH4G_EU:
            self._cipher = Blowfish.new(b'AgK2DYheaCjyHGPB')
        elif game == MH4G_JP:
            self._cipher = Blowfish.new(b'AgK2DYheaCjyHGP8')
        elif game == MH4G_KR:
            self._cipher = Blowfish.new(b'AgK2DYheaOjyHGP8')
        else:
            raise ValueError('Ivalid game selected.')

    def encrypt(self, buff):
        buff += hashlib.sha1(buff).digest()
        size = len(buff)
        if len(buff) % 8 != 0:
            buff += b'\x00' * (8 - len(buff) % 8)
        buff = array.array('I', buff)
        buff.byteswap()
        buff = array.array('I', self._cipher.encrypt(buff.tostring()))
        buff.append(size)
        buff.byteswap()
        return buff.tostring()

    def decrypt(self, buff):
        buff = array.array('I', buff)
        buff.byteswap()
        size = buff.pop()
        if size > len(buff) * 4:
            raise ValueError('Invalid file size in footer.')
        buff = array.array('I', self._cipher.decrypt(buff.tostring()))
        buff.byteswap()
        buff = buff.tostring()[:size]
        md = buff[-20:]
        buff = buff[:-20]
        if md != hashlib.sha1(buff).digest():
            raise ValueError('Invalid SHA1 hash in footer.')
        return buff

    def encrypt_file(self, dlc_file, out_file):
        dlc = open(dlc_file, 'rb').read()
        dlc = self.encrypt(dlc)
        open(out_file, 'wb').write(dlc)

    def decrypt_file(self, dlc_file, out_file):
        dlc = open(dlc_file, 'rb').read()
        dlc = self.decrypt(dlc)
        open(out_file, 'wb').write(dlc)

