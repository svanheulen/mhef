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
import math
import random

from Crypto.Cipher import Blowfish
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


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
MH4G_TW = 10
MHX_JP = 11
MHX_NA = 12
MHX_EU = 13

MH4G_SD_NORMAL = 0
MH4G_SD_CARD = 1
MH4G_SD_QUEST = 2


class SavedataCipher:
    def __init__(self, game):
        if game in (MH4G_JP, MH4G_NA, MH4G_EU, MH4G_KR, MH4G_TW):
            self._cipher = Blowfish.new(b'blowfish key iorajegqmrna4itjeangmb agmwgtobjteowhv9mope')
        elif game == MH4_JP:
            self._cipher = None
        else:
            raise ValueError('Invalid game selected.')

    def _xor(self, buff, key):
        buff = array.array('H', buff)
        for i in range(len(buff)):
            if key == 0:
                key = 1
            key = key * 0xb0 % 0xff53
            buff[i] ^= key
        return buff.tostring()

    def encrypt(self, buff, type=MH4G_SD_NORMAL):
        csum = sum(bytearray(buff)) & 0xffffffff
        buff = array.array('I', buff)
        buff.insert(0, csum)
        seed = random.getrandbits(16)
        buff = array.array('I', self._xor(buff.tostring(), seed))
        buff.insert(0, (seed << 16) + 0x10)
        header = buff[:6]
        if type == MH4G_SD_CARD:
            buff = buff[6:]
        if self._cipher:
            buff.byteswap()
            buff = array.array('I', self._cipher.encrypt(buff.tostring()))
            buff.byteswap()
        if type == MH4G_SD_CARD:
            buff = header + buff
        buff = buff.tostring()
        if type == MH4G_SD_QUEST:
            buff += b'\x00' * 0x100
        return buff

    def decrypt(self, buff, type=MH4G_SD_NORMAL):
        if type == MH4G_SD_QUEST:
            buff = buff[:-0x100]
        buff = array.array('I', buff)
        header = buff[:6]
        if type == MH4G_SD_CARD:
            buff = buff[6:]
        if self._cipher:
            buff.byteswap()
            buff = array.array('I', self._cipher.decrypt(buff.tostring()))
            buff.byteswap()
        if type == MH4G_SD_CARD:
            buff = header + buff
        seed = buff.pop(0) >> 16
        buff = array.array('I', self._xor(buff.tostring(), seed))
        csum = buff.pop(0)
        buff = buff.tostring()
        if csum != (sum(bytearray(buff)) & 0xffffffff):
            raise ValueError('Invalid checksum in header.')
        return buff

    def encrypt_file(self, savedata_file, out_file, type=MH4G_SD_NORMAL):
        savedata = open(savedata_file, 'rb').read()
        savedata = self.encrypt(savedata, type)
        open(out_file, 'wb').write(savedata)

    def decrypt_file(self, savedata_file, out_file, type=MH4G_SD_NORMAL):
        savedata = open(savedata_file, 'rb').read()
        savedata = self.decrypt(savedata, type)
        open(out_file, 'wb').write(savedata)


class DLCCipher:
    def __init__(self, game):
        if game == MH4G_NA or game == MH4G_EU:
            self._cipher = Blowfish.new(b'AgK2DYheaCjyHGPB')
        elif game == MH4G_JP:
            self._cipher = Blowfish.new(b'AgK2DYheaCjyHGP8')
        elif game == MH4G_KR:
            self._cipher = Blowfish.new(b'AgK2DYheaOjyHGP8')
        elif game == MH4G_TW:
            self._cipher = Blowfish.new(b'Capcom123 ')
        else:
            raise ValueError('Invalid game selected.')

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


class DLCXCipher:
    def __init__(self, game, key, pubkey=None):
        self._cipher = Blowfish.new(key.encode())
        self._pubkey = None
        if pubkey is not None:
            self._pubkey = RSA.importKey(pubkey)
        if game == MHX_NA or game == MHX_EU:
            self._static_pubkey = RSA.importKey(b'0\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\xa9\x88\x82{\xc7\xbeV\xbe\xaa(\x89\xb0\x96\x18\x82\xab\x96U\xb3q\x89\xbd\xff\x83\xbe\x03\x1aJ8s\xce\xe8S\xc9+\xf2N\xfa\xf9\x0c!\xeaj\xf3&\x1e)\x10n[\xf5L\xac\x03\x06\x8c\xddW\xe1\xf80g&\x17/\x0cT\x18\x8e\x1f\xbc\xec\xab\x11\x11/)S\x06\x9c\x05\xa6t\xd2\x8f\x9c\xca\x80\x02yy,\x89\xb02\x16\x91.\xca\xe2\xd3\xcb]z\xab\xa5_\x85\xb9\xe1\xf7v\x1c\x02D\x7fC\x8f\x0c\x1bc\x885{\x1e\xab\xe0AH\x9b\xe5@\xf0n\x01]\x17a\x1f\x82X\xed\'L\xee!\xd2~\xbd\x9eb\x8d\'\x8d\x8c+CH\xd3\xa1\x1d\x03\xcb\x06\x9a\x80\xd7\xf7\x0c,\xfc\x1a=j\xce\xea\xfb\xa0\xeb\r\x022\x93\x7f\xc7x\x164\xf1\'\xe6.\x16|\xefn!\xe2Z\xef\xb7\xb6<:\x8b;\xaf\xd4X\xa1\xb0p\x92\r\x8f\nKg d\xf7\xdb\xb6\xe8\xae\x92,\xa1\xd9\xaa\xa31\xda\xe7\xbc`#-R\xccp\x99|\x1c\xfb\xbf6\x1ck\x8eBj\xb4S\xe9\xfb\x02\x03\x01\x00\x01')
            self._sigs = True
        elif game == MHX_JP:
            self._sigs = False
        else:
            raise ValueError('Invalid game selected.')

    def _gen_xor_buff(self, seed, buff_len):
        xor_buff = array.array('I')
        for i in range(int(math.ceil(buff_len/8.0))):
            xor_buff.extend([seed, i])
        xor_buff = array.array('I', self._cipher.encrypt(xor_buff.tostring()))
        xor_buff.byteswap()
        return bytearray(xor_buff.tostring())

    def encrypt(self, buff):
        seed = random.getrandbits(32)
        buff = bytearray(buff)
        buff.extend(hashlib.sha1(buff).digest())
        xor_buff = self._gen_xor_buff(seed, len(buff))
        for i in range(len(buff)):
            buff[i] ^= xor_buff[i]
        seed = array.array('I', [seed])
        seed.byteswap()
        if self._sigs:
            return bytes(buff) + seed.tostring() + b'\x00' * 0x200
        return bytes(buff) + seed.tostring()

    def decrypt(self, buff):
        if self._sigs:
            md = SHA256.new(buff[:-0x100])
            verifier = PKCS1_v1_5.new(self._static_pubkey)
            if verifier.verify(md, buff[-0x100:]) == False:
                raise ValueError('Invalid signature in footer.')
            if self._pubkey is not None:
                md = SHA256.new(buff[:-0x200])
                verifier = PKCS1_v1_5.new(self._pubkey)
                if verifier.verify(md, buff[-0x200:-0x100]) == False:
                    raise ValueError('Invalid signature in footer.')
            buff = buff[:-0x200]
        seed = array.array('I', buff[-4:])
        seed.byteswap()
        seed = seed[0]
        buff = bytearray(buff[:-4])
        xor_buff = self._gen_xor_buff(seed, len(buff))
        for i in range(len(buff)):
            buff[i] ^= xor_buff[i]
        md = buff[-20:]
        buff = bytes(buff[:-20])
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

