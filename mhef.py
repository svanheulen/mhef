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

import array
import hashlib
import os
import random


MHP2_JP = 0
MHP2_NA = 1
MHP2_EU = 2
MHP2G_JP = 3
MHP2G_NA = 4
MHP2G_EU = 5
MHP3_JP = 6


class DataCipher:
    _encode_table = b'\xc0\xa8\xca\x07KnHo\xd6\x921,\x9d\xfb\xe1Pa\xc6\xe4R>\x12\xad3\xae\xeb\xf3/ki{S\x96\xc4\xb1\x9c\x1c\xc5 \x86\x19\x13\xe9j&ux\x8cC\xedzf]\x18\x1d\xe8p\xa5^\xf2_X\x05F\r\x97\x9e|\xeae\xdd$\x8fIB\xaf\xf4%\xb8+\x08r\x17\xd9\xa4\xd3\x93q[@\xb2.\x0b~L\x04\xf7\x11\xc17y\xa7)\xbc\x1bV\x8b\xfa\x8d6;m\xd4W\x83\xbd\x1f\xd7b\x84\xf5\xda\xd5\xab\xcc\xa2G\x88\x9a-\xc7\xdf\xcb\x02(A\xa9=\xd8\xa1#<\x81l\\\xd0h\xc9\xbf\x99\x01\xbe\xf9\xfc\xec\xb7\n\x82\x89\xdc\x91\xef\x14\xcf4J\x03\xd1\xba5\x8a\x06\xff8\xa0\xf0\xce}\x0cv\xc2\xb3\xac\t\x94UT\x80\xa3\x95\xbb\xa60*\xf6g\x1e\xfewcd\x87`\x00\xb0\x98D\xeeM\xe5\xc3\xcdQ"s\x9b\xe0\x1at\xc8Z?N\xe6\xaa\x7f!\xf1Y\x9f\xb9\x90O\xe2\xfd\xb4\x16\xe3\xf8\x0e\xe7\x15\x859:\xde\x0f\xd2\xb6\x8e\'\xdb\xb52E\x10'
    _decode_table = b'\xcb\x96\x85\xa6_>\xab\x03P\xb7\x9c\\\xb2@\xef\xf6\xffa\x15)\xa2\xf1\xecR5(\xd9h$6\xc4t&\xe2\xd5\x8cGM,\xfa\x86f\xc1O\x0b\x81[\x1b\xc0\n\xfd\x17\xa4\xa9mc\xad\xf3\xf4n\x8d\x89\x14\xddY\x87J0\xce\xfe?~\x06I\xa5\x04^\xd0\xde\xe8\x0f\xd4\x13\x1f\xba\xb9iq=\xe4\xdcX\x904:<\xca\x10v\xc7\xc8E3\xc3\x92\x1d+\x1c\x8fo\x05\x078WQ\xd6\xda-\xb3\xc6.d2\x1eC\xb1]\xe1\xbb\x8e\x9drw\xf2\'\xc9\x7f\x9e\xaaj/l\xf9H\xe7\xa0\tV\xb8\xbd A\xcd\x95\x80\xd7#\x0cB\xe5\xae\x8b}\xbcT9\xbfe\x01\x88\xe0{\xb6\x16\x18K\xcc"Z\xb5\xeb\xfc\xf8\x9bN\xe6\xa8\xbegs\x97\x94\x00b\xb4\xd2!%\x11\x82\xdb\x93\x02\x84|\xd3\xb0\xa3\x91\xa7\xf7Upz\x08u\x8aSy\xfb\x9fF\xf5\x83\xd8\x0e\xe9\xed\x12\xd1\xdf\xf07*D\x19\x9a1\xcf\xa1\xaf\xe3;\x1aLx\xc2`\xee\x98k\r\x99\xea\xc5\xac'
    _key_default = (0x2345, 0x7f8d)
    _key_modifier = (0xffd9, 0xfff1)
    _mhp2g_exceptions = ()
    _mhp3_exceptions = (17, 18, 19, 20, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92)

    def __init__(self, game):
        self._key = [0, 0]
        if game >= MHP2G_JP and game <= MHP2G_EU:
            self._exceptions = self._mhp2g_exceptions
        elif game == MHP3_JP:
            self._exceptions = self._mhp3_exceptions
        else:
            raise ValueError('Invalid game selected.')

    def _init_key(self, seed):
        self._key[0] = seed >> 16;
        if self._key[0] == 0:
            self._key[0] = self._key_default[0]
        self._key[1] = seed & 0xffff
        if self._key[1] == 0:
            self._key[1] = self._key_default[1]

    def _next_key(self):
        self._key[0] *= self._key_default[0]
        self._key[0] %= self._key_modifier[0]
        self._key[1] *= self._key_default[1]
        self._key[1] %= self._key_modifier[1]
        return (self._key[0] << 16) + self._key[1]

    def encrypt(self, buff, lba):
        buff = array.array('I', buff)
        self._init_key(lba)
        for i in range(len(buff)):
            buff[i] ^= self._next_key()
        return buff.tobytes().translate(self._encode_table)

    def decrypt(self, buff, lba):
        buff = array.array('I', buff.translate(self._decode_table))
        self._init_key(lba)
        for i in range(len(buff)):
            buff[i] ^= self._next_key()
        return buff.tobytes()

    def encrypt_file(self, data_file, out_file):
        with open(data_file, 'rb') as data, open(out_file, 'wb') as out:
            toc_size = array.array('I', data.read(4))[0] * 2048
            file_size = data.seek(0, os.SEEK_END)
            data.seek(0)
            toc = data.read(toc_size)
            out.write(self.encrypt(toc, 0))
            toc = array.array('I', toc)
            file_count = toc.index(file_size // 2048)
            for i in range(file_count):
                data.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                buff = data.read((toc[i+1] - toc[i]) * 2048)
                if i in self._exceptions:
                    out.write(buff)
                else:
                    out.write(self.encrypt(buff, toc[i]))

    def decrypt_file(self, data_file, out_file):
        with open(data_file, 'rb') as data, open(out_file, 'wb') as out:
            toc_size = self.decrypt(data.read(4), 0)
            toc_size = array.array('I', toc_size)[0] * 2048
            file_size = data.seek(0, os.SEEK_END)
            data.seek(0)
            toc = self.decrypt(data.read(toc_size), 0)
            out.write(toc)
            toc = array.array('I', toc)
            file_count = toc.index(file_size // 2048)
            for i in range(file_count):
                data.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                buff = data.read((toc[i+1] - toc[i]) * 2048)
                if i in self._exceptions:
                    out.write(buff)
                else:
                    out.write(self.decrypt(buff, toc[i]))


class SavedataCipher(DataCipher):
    _encode_table = b'\xa9<\xdd\x96\xfe\x8e\x07\xcd\xdf\xa2\x87\x82\xd4\x84\xb5}\xe4\xf7\xf0\xa5Mz\r\x11=\xffB\xb8\x13\xfc\xd1\xf5O\x01\x02l1c7G\x19"\xb9\x86\xf1\x1f\x0f5\xce(&\x0e*\x9aQ\xb4\x91\x17XS\\\x04\xeb\x8btV\xb2\xe9\x9c0Yg\x97\xd3LA\xbf-\xb3R\x12\xfb|\xa0\t\xa6q\xcb{8\x10DZk\x8a\x1eu+!^\xda\xed`\x7f\x8d\xc3\xa3\xea\xdew\xef\xe0)\x8cn\x16i\x0b\n\xa4 \xbaC\xca\x9d~e\x93\x89o\x9e\x95_W\x8f\x08\xbe\xe2\xdbjp\xe6\xf8m\xcc\xe8\xcf\x9f\xf2?\xaf\xfd\x1d\xf3Nh\xaa\xb7\xad\x889>v\xa1\xd6;\x00\xb0\xe5\xbdd\xc1\xc6K,\x15y\xf9J\xd8\xab\x18\xc9\xd0\xd5P\xe7\x90\xae:\xa8\xbb\xe3\xc8/fa\xc2r\xdc\xf6#T[\'\x1c\x92\x83\xc0\xc4\x81\x98s\xec\x8546\x1a\xd2E\xbc\xa7\x14\x9b\xee\xc5\xb1\xacUxH\xfa\xf4\xc7%b]\x0c@\x80F\x1b\xd9\x94I\x06\xb6\xe12\x03\x99\x053$.\xd7'
    _decode_table = b'\xa6!"\xf9=\xfb\xf5\x06\x87Tvu\xed\x163.Z\x17P\x1c\xde\xafs9\xb5(\xd9\xf1\xcd\x98_-xb)\xc9\xfd\xea2\xcc1p4a\xaeM\xfe\xc2E$\xf8\xfc\xd7/\xd8&Y\xa0\xbd\xa5\x01\x18\xa1\x95\xeeK\x1az[\xdb\xf0\'\xe6\xf4\xb2\xadJ\x14\x9a \xb96O;\xca\xe4A\x85:F\\\xcb<\xecc\x84f\xc4\xeb%\xaa~\xc3G\x9bt\x8b]#\x8fr\x81\x8cV\xc6\xd4@`\xa2m\xe5\xb0\x15XR\x0f}g\xef\xd2\x0b\xcf\r\xd6+\n\x9f\x80^?qh\x05\x86\xbb8\xce\x7f\xf3\x83\x03H\xd3\xfa5\xdfD|\x82\x93S\xa3\tjw\x13U\xdd\xbe\x00\x9c\xb4\xe3\x9e\xbc\x96\xa7\xe2BN7\x0e\xf6\x9d\x1b*y\xbf\xdc\xa9\x88L\xd0\xab\xc5i\xd1\xe1\xac\xe9\xc1\xb6{W\x90\x070\x92\xb7\x1e\xdaI\x0c\xb8\xa4\xff\xb3\xf2d\x8a\xc7\x02l\x08o\xf7\x89\xc0\x10\xa8\x8d\xba\x91Ck>\xd5e\xe0n\x12,\x94\x99\xe8\x1f\xc8\x11\x8e\xb1\xe7Q\x1d\x97\x04\x19'
    _key_default = (0xdfa3, 0x215f)
    _key_modifier = (0xffef, 0xff8f)
    _mhp2g_jp_hash_salt = b'S)R?Bf8xW3#5h9lGU8wR'
    _mhp2g_na_hash_salt = b'3Nc94Hq1zOLh8d62Sb69'
    _mhp3_jp_hash_salt = b'VQ(DOdIO9?X3!2GmW#XF'

    def __init__(self, game):
        self._key = [0, 0]
        if game == MHP2G_JP:
            self._hash_salt = self._mhp2g_jp_hash_salt
        elif game == MHP2G_NA or game == MHP2G_EU:
            self._hash_salt = self._mhp2g_na_hash_salt
        elif game == MHP3_JP:
            self._hash_salt = self._mhp3_jp_hash_salt
        else:
            raise ValueError('Invalid game selected.')

    def encrypt(self, buff):
        buff += hashlib.sha1(buff[:-12] + self._hash_salt).digest()
        seed = random.getrandbits(16)
        buff = DataCipher.encrypt(self, buff.translate(self._encode_table), seed)
        seed = array.array('I', [seed]).tobytes()
        return buff + seed.translate(self._encode_table).translate(self._encode_table)

    def decrypt(self, buff):
        seed = buff[-4:].translate(self._decode_table).translate(self._decode_table)
        buff = DataCipher.decrypt(self, buff[:-4], array.array('I', seed)[0])
        buff = buff.translate(self._decode_table)
        md = buff[-20:]
        buff = buff[:-20]
        if md != hashlib.sha1(buff[:-12] + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return buff

    def encrypt_file(self, savedata_file, out_file):
        with open(savedata_file, 'rb') as savedata, open(out_file, 'wb') as out:
            out.write(self.encrypt(savedata.read()))

    def decrypt_file(self, savedata_file, out_file):
        with open(savedata_file, 'rb') as savedata, open(out_file, 'wb') as out:
            out.write(self.decrypt(savedata.read()))


class PSPSavedataCipher:
    _hash_key_6 = b'pD\xa3\xae\xef]\xa5\xf2\x85\x7f\xf2\xd6\x94\xf56;'
    _hash_key_7 = b'\xecm)Y&5\xa5\x7f\x97*\r\xbc\xa3&3\x00'
    _aes_key_10 = b']\xc7\x119\xd0\x198\xbc\x02\x7f\xdd\xdc\xb0\x83}\x9d'
    _aes_key_19 = b'\x03\xb3\x02\xe8_\xf3\x81\xb1;\x8d\xaa*\x90\xff^a'
    _mhp2_jp_key = b'\xe3\xb5\xce\xfa\xe8N\xb0\xa1\x85\x9a\xb7\x1b\xdd\xe6\xd8\xf3'
    _mhp2_na_key = b'\xb9\xa9\x00\x9do\xc2\xb4\xeb\xf4\xf8\xca\xb2\xd7r\xe9\xab'
    _mhp2g_jp_key = b'\xcd\x1f Y\xaep\xefh\xdc\xa2E\x13\xb4Z\xdb\n'
    _mhp2g_na_key = b'J\x1f\xf3Y\xae\xb6\xef\xf8\x1c\xa8\xcb#\xbc\xa5{\xb3'
    _mhp3_jp_key = b"\xe3\x05\xce\xfa\xebF\xb01\x85\x9a'[\xdf2\xd8c"

    def __init__(self, game):
        crypto = __import__('Crypto.Cipher', fromlist=('AES',))
        self._AES = crypto.AES
        if game == MHP2_JP:
            self._key = self._mhp2_jp_key
        elif game == MHP2_NA or game == MHP2_EU:
            self._key = self._mhp2_na_key
        elif game == MHP2G_JP:
            self._key = self._mhp2g_jp_key
        elif game == MHP2G_NA or game == MHP2G_EU:
            self._key = self._mhp2g_na_key
        elif game == MHP3_JP:
            self._key = self._mhp3_jp_key
        else:
            raise ValueError('Invalid game selected.')

    def encrypt(self, buf):
        xor_key = os.urandom(16)
        xor_buf = bytearray()
        for i in range(1, len(buf) // 16 + 1):
            xor_buf.extend(xor_key[:12])
            xor_buf.extend(array.array('I', [i]).tobytes())
        aes = self._AES.new(self._aes_key_19, self._AES.MODE_CBC, b'\x00'*16)
        xor_buf = aes.decrypt(bytes(xor_buf))
        out_buf = bytearray(buf)
        for i in range(len(out_buf)):
            out_buf[i] ^= xor_buf[i]
        xor_key = [(xor_key[i] ^ self._hash_key_6[i]) for i in range(16)]
        aes = self._AES.new(self._aes_key_10, self._AES.MODE_CBC, b'\x00'*16)
        xor_key = aes.encrypt(bytes(xor_key))
        xor_key = [(xor_key[i] ^ self._hash_key_7[i]) for i in range(16)]
        xor_key = [(xor_key[i] ^ self._key[i]) for i in range(16)]
        return bytes(xor_key) + bytes(out_buf)

    def decrypt(self, buf):
        xor_key = [(buf[i] ^ self._key[i]) for i in range(16)]
        xor_key = [(xor_key[i] ^ self._hash_key_7[i]) for i in range(16)]
        aes = self._AES.new(self._aes_key_10, self._AES.MODE_CBC, b'\x00'*16)
        xor_key = aes.decrypt(bytes(xor_key))
        xor_key = [(xor_key[i] ^ self._hash_key_6[i]) for i in range(12)]
        xor_buf = bytearray()
        for i in range(1, len(buf) // 16):
            xor_buf.extend(xor_key)
            xor_buf.extend(array.array('I', [i]).tobytes())
        aes = self._AES.new(self._aes_key_19, self._AES.MODE_CBC, b'\x00'*16)
        xor_buf = aes.decrypt(bytes(xor_buf))
        out_buf = bytearray(buf[16:])
        for i in range(len(out_buf)):
            out_buf[i] ^= xor_buf[i]
        return bytes(out_buf)

    def encrypt_file(self, pspsavedata_file, out_file):
        with open(pspsavedata_file, 'rb') as pspsavedata, open(out_file, 'wb') as out:
            out.write(self.encrypt(pspsavedata.read()))

    def decrypt_file(self, pspsavedata_file, out_file):
        with open(pspsavedata_file, 'rb') as pspsavedata, open(out_file, 'wb') as out:
            out.write(self.decrypt(pspsavedata.read()))


class QuestCipher:
    _mhp2g_key_default = (0xff9d, 0xffa9, 0xffc7, 0xfff1)
    _mhp3_key_default = (0xffa9, 0xff9d, 0xfff1, 0xffc7)
    _mhp2g_key_modifier = (0x1709, 0x3df3, 0x747b, 0xb381)
    _mhp3_key_modifiet = (0x3df3, 0x1709, 0xb381, 0x747b)
    _mhp2g_jp_hash_salt = b'37wyS2Jfc3x5w9oG'
    _mhp2g_na_hash_salt = b'Vd6gh8F30wA86Ex5'
    _mhp3_jp_hash_salt =b'sR2Tf4eLAj8b3TH7'

    def __init__(self, game):
        self._key = [0, 0, 0, 0]
        if game == MHP2G_JP:
            self._key_default = self._mhp2g_key_default
            self._key_modifier = self._mhp2g_key_modifier
            self._hash_salt = self._mhp2g_jp_hash_salt
        elif game == MHP2G_NA or game == MHP2G_EU:
            self._key_default = self._mhp2g_key_default
            self._key_modifier = self._mhp2g_key_modifier
            self._hash_salt = self._mhp2g_na_hash_salt
        elif game == MHP3_JP:
            self._key_default = self._mhp3_key_default
            self._key_modifier = self._mhp3_key_modifier
            self._hash_salt = self._mhp3_jp_hash_salt
        else:
            raise ValueError('Invalid game selected.')

    def _init_key(self, seed, num):
        self._key[num] = seed
        if self._key[num] == 0:
            self._key[num] = self._key_default[num]

    def _next_key(self, num):
        self._key[num] *= self._key_modifier[num]
        self._key[num] %= self._key_default[num]
        return self._key[num]

    def csum(self, buff):
        return sum(buff) & 0xffff

    def encrypt(self, buff):
        buff = array.array('I', [len(buff)]).tobytes() + hashlib.sha1(buff + self._hash_salt).digest() + buff
        buff = array.array('H', buff)
        seed = []
        for i in range(4):
            seed.insert(0, random.getrandbits(16))
            self._init_key(seed[0], i)
        for i in range(len(buff)):
            buff[i] ^= self._next_key(i%4)
        for i in range(4):
            buff.insert(0, seed[i])
        return buff.tobytes()

    def decrypt(self, buff):
        buff = array.array('H', buff)
        for i in range(4):
            self._init_key(buff.pop(0), i)
        for i in range(len(buff)):
            buff[i] ^= self._next_key(i%4)
        buff = buff.tobytes()
        size = array.array('I', buff[:4])[0]
        md = buff[4:24]
        buff = buff[24:]
        if size != len(buff):
            raise ValueError('Invalid file size in header.')
        if md != hashlib.sha1(buff + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return buff

    def encrypt_file(self, quest_file, out_file):
        with open(quest_file, 'rb') as quest, open(out_file, 'wb') as out:
            buff = self.encrypt(quest.read())
            out.write(buff)
            return self.csum(buff)

    def decrypt_file(self, quest_file, out_file):
        with open(quest_file, 'rb') as quest, open(out_file, 'wb') as out:
            buff = quest.read()
            out.write(self.decrypt(buff))
            return self.csum(buff)

