# Copyright 2013-2015 Seth VanHeulen
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

"""
Monster Hunter encryption functions module.

This module provides the various encryption functions used in Monster Hunter
games for the Playstation Portable.

Constants:
MHP_JP -- Identifier for Monster Hunter Portable (ULJM-05066)
MHP_NA -- Identifier for Monster Hunter Freedom (ULUS-10084)
MHP_EU -- Identifier for Monster Hunter Freedom (ULES-00318)
MHP2_JP -- Identifier for Monster Hunter Portable 2nd (ULJM-05156)
MHP2_NA -- Identifier for Monster Hunter Freedom 2 (ULUS-10266)
MHP2_EU -- Identifier for Monster Hunter Freedom 2 (ULES-00851)
MHP2G_JP -- Identifier for Monster Hunter Portable 2nd G (ULJM-05500)
MHP2G_NA -- Identifier for Monster Hunter Freedom Unite (ULUS-10391)
MHP2G_EU -- Identifier for Monster Hunter Freedom Unite (ULES-01213)
MHP2_JP -- Identifier for Monster Hunter Portable 3rd (ULJM-05800)

Classes:
DataCipher -- Cipher for Monster Hunter data files
SavedataCipher -- Cipher for Monster Hunter save files
PSPSavedataCipher -- Cipher for Playstation Portable save files
QuestCiper -- Cipher for Monster Hunter quest files
BonusCipher -- Cipher for Monster Hunter bonus files

"""

import array
import hashlib
import os
import random
import struct

from Crypto.Cipher import AES


MHP_JP = -3
MHP_NA = -2
MHP_EU = -1
MHP2_JP = 0
MHP2_NA = 1
MHP2_EU = 2
MHP2G_JP = 3
MHP2G_NA = 4
MHP2G_EU = 5
MHP3_JP = 6


class DataCipher:
    """
    Cipher for Monster Hunter data files.

    This class provides encryption functions for the main DATA.BIN file found
    on the UMDs of the 3rd and 2nd G versions of Monster Hunter.

    Methods:
    encrypt -- Return an encrypted copy of the given data blocks
    decrypt -- Return a decrypted copy of the given data blocks
    encrypt_file -- Save an encrypted copy of the given DATA.BIN file
    decrypt_file -- Save a decrypted copy of the given DATA.BIN file

    """

    _encode_table = b'\xc0\xa8\xca\x07KnHo\xd6\x921,\x9d\xfb\xe1Pa\xc6\xe4R>' \
            b'\x12\xad3\xae\xeb\xf3/ki{S\x96\xc4\xb1\x9c\x1c\xc5 \x86\x19' \
            b'\x13\xe9j&ux\x8cC\xedzf]\x18\x1d\xe8p\xa5^\xf2_X\x05F\r\x97' \
            b'\x9e|\xeae\xdd$\x8fIB\xaf\xf4%\xb8+\x08r\x17\xd9\xa4\xd3\x93q[' \
            b'@\xb2.\x0b~L\x04\xf7\x11\xc17y\xa7)\xbc\x1bV\x8b\xfa\x8d6;m' \
            b'\xd4W\x83\xbd\x1f\xd7b\x84\xf5\xda\xd5\xab\xcc\xa2G\x88\x9a-' \
            b'\xc7\xdf\xcb\x02(A\xa9=\xd8\xa1#<\x81l\\\xd0h\xc9\xbf\x99\x01' \
            b'\xbe\xf9\xfc\xec\xb7\n\x82\x89\xdc\x91\xef\x14\xcf4J\x03\xd1' \
            b'\xba5\x8a\x06\xff8\xa0\xf0\xce}\x0cv\xc2\xb3\xac\t\x94UT\x80' \
            b'\xa3\x95\xbb\xa60*\xf6g\x1e\xfewcd\x87`\x00\xb0\x98D\xeeM\xe5' \
            b'\xc3\xcdQ"s\x9b\xe0\x1at\xc8Z?N\xe6\xaa\x7f!\xf1Y\x9f\xb9\x90O' \
            b'\xe2\xfd\xb4\x16\xe3\xf8\x0e\xe7\x15\x859:\xde\x0f\xd2\xb6\x8e' \
            b'\'\xdb\xb52E\x10'
    _decode_table = b'\xcb\x96\x85\xa6_>\xab\x03P\xb7\x9c\\\xb2@\xef\xf6\xff' \
            b'a\x15)\xa2\xf1\xecR5(\xd9h$6\xc4t&\xe2\xd5\x8cGM,\xfa\x86f\xc1' \
            b'O\x0b\x81[\x1b\xc0\n\xfd\x17\xa4\xa9mc\xad\xf3\xf4n\x8d\x89' \
            b'\x14\xddY\x87J0\xce\xfe?~\x06I\xa5\x04^\xd0\xde\xe8\x0f\xd4' \
            b'\x13\x1f\xba\xb9iq=\xe4\xdcX\x904:<\xca\x10v\xc7\xc8E3\xc3\x92' \
            b'\x1d+\x1c\x8fo\x05\x078WQ\xd6\xda-\xb3\xc6.d2\x1eC\xb1]\xe1' \
            b'\xbb\x8e\x9drw\xf2\'\xc9\x7f\x9e\xaaj/l\xf9H\xe7\xa0\tV\xb8' \
            b'\xbd A\xcd\x95\x80\xd7#\x0cB\xe5\xae\x8b}\xbcT9\xbfe\x01\x88' \
            b'\xe0{\xb6\x16\x18K\xcc"Z\xb5\xeb\xfc\xf8\x9bN\xe6\xa8\xbegs' \
            b'\x97\x94\x00b\xb4\xd2!%\x11\x82\xdb\x93\x02\x84|\xd3\xb0\xa3' \
            b'\x91\xa7\xf7Upz\x08u\x8aSy\xfb\x9fF\xf5\x83\xd8\x0e\xe9\xed' \
            b'\x12\xd1\xdf\xf07*D\x19\x9a1\xcf\xa1\xaf\xe3;\x1aLx\xc2`\xee' \
            b'\x98k\r\x99\xea\xc5\xac'
    _key_default = (0x2345, 0x7f8d)
    _key_modifier = (0xffd9, 0xfff1)
    _mhp2g_jp_exceptions = (22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42)
    _mhp2g_na_exceptions = (42, 43, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)
    _mhp3_jp_exceptions = (17, 18, 19, 20, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92)

    def __init__(self, game):
        """
        Initialize the cipher for the given game.

        Arguments:
        game -- Identifier of a version of Monster Hunter

        """
        self._key = [0, 0]
        # Select which files are unencrypted
        if game == MHP2G_JP:
            self._exceptions = self._mhp2g_jp_exceptions
        if game == MHP2G_NA or game == MHP2G_EU:
            self._exceptions = self._mhp2g_na_exceptions
        elif game == MHP3_JP:
            self._exceptions = self._mhp3_jp_exceptions
        else:
            raise ValueError('Invalid game selected.')

    def _init_key(self, seed):
        # Initialize the XOR cipher key using a seed
        self._key[0] = seed >> 16
        if self._key[0] == 0:
            self._key[0] = self._key_default[0]
        self._key[1] = seed & 0xffff
        if self._key[1] == 0:
            self._key[1] = self._key_default[1]

    def _next_key(self):
        # Calculate a new XOR cipher key based on the previous key
        self._key[0] *= self._key_default[0]
        self._key[0] %= self._key_modifier[0]
        self._key[1] *= self._key_default[1]
        self._key[1] %= self._key_modifier[1]
        return (self._key[0] << 16) + self._key[1]

    def encrypt(self, buff, lba):
        """
        Return an encrypted copy of the given data blocks.

        Arguments:
        buff -- Data blocks read from a decrypted DATA.BIN file
        lba -- Block address of the given data blocks

        """
        buff = array.array('I', buff)
        # Use the block address to seed the XOR cipher key
        self._init_key(lba)
        # Apply an XOR cipher to the data using a new key every 4 bytes
        for i in range(len(buff)):
            buff[i] ^= self._next_key()
        # Apply a substitution cipher to the data using the encode table
        return buff.tostring().translate(self._encode_table)

    def decrypt(self, buff, lba):
        """
        Return a decrypted copy of the given data blocks.

        Arguments:
        buff -- Data blocks read from an encrypted DATA.BIN file
        lba -- Block address of the given data blacks

        """
        # Apply a substitution cipher to the data using the decode table
        buff = array.array('I', buff.translate(self._decode_table))
        # Use the block address to seed the XOR cipher key
        self._init_key(lba)
        # Apply an XOR cipher to the data using a new key every 4 bytes
        for i in range(len(buff)):
            buff[i] ^= self._next_key()
        return buff.tostring()

    def encrypt_file(self, data_file, out_file):
        """
        Save an encrypted copy of the given DATA.BIN file.

        Arguments:
        data_file -- Path to a decrypted DATA.BIN file
        out_file -- Path to save the encrypted DATA.BIN file

        """
        with open(data_file, 'rb') as data, open(out_file, 'wb') as out:
            # Get the block address of the first file to determine the size of
            # the table of contents
            toc_size = array.array('I', data.read(4))[0] * 2048
            file_size = data.seek(0, os.SEEK_END)
            data.seek(0)
            toc = data.read(toc_size)
            # Encrypt the table of contents
            out.write(self.encrypt(toc, 0))
            toc = array.array('I', toc)
            # Find the number of files by getting the index of the table of
            # contents entry pointing to the end of the file
            file_count = toc.index(file_size // 2048)
            # Encrypt each file in the data file
            for i in range(file_count):
                data.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                buff = data.read((toc[i+1] - toc[i]) * 2048)
                # Skip encryption of certain files
                if i in self._exceptions:
                    out.write(buff)
                else:
                    out.write(self.encrypt(buff, toc[i]))

    def decrypt_file(self, data_file, out_file):
        """
        Save a decrypted copy of the given DATA.BIN file.

        Arguments:
        data_file -- Path to an encrypted DATA.BIN file
        out_file -- Path to save the decrypted DATA.BIN file

        """
        with open(data_file, 'rb') as data, open(out_file, 'wb') as out:
            # Decrypt the block address of the first file to determine the size
            # of the table of contents
            toc_size = self.decrypt(data.read(4), 0)
            toc_size = array.array('I', toc_size)[0] * 2048
            file_size = data.seek(0, os.SEEK_END)
            data.seek(0)
            # Decrypt the table of contents
            toc = self.decrypt(data.read(toc_size), 0)
            out.write(toc)
            toc = array.array('I', toc)
            # Find the number of files by getting the index of the table of
            # contents entry pointing to the end of the file
            file_count = toc.index(file_size // 2048)
            # Decrypt each file in the data file
            for i in range(file_count):
                data.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                buff = data.read((toc[i+1] - toc[i]) * 2048)
                # Skip decryption of certain files
                if i in self._exceptions:
                    out.write(buff)
                else:
                    out.write(self.decrypt(buff, toc[i]))


class SavedataCipher(DataCipher):
    """
    Cipher for Monster Hunter save files.

    This class provides encryption functions for save files from the 3rd and
    2nd G versions of Monster Hunter.

    Methods:
    encrypt -- Return an encrypted copy of the given save file data
    decrypt -- Return a decrypted copy of the given save file data
    encrypt_file -- Save an encrypted copy of the given save file
    decrypt_file -- Save a decrypted copy of the given save file

    """

    _encode_table = b'\xa9<\xdd\x96\xfe\x8e\x07\xcd\xdf\xa2\x87\x82\xd4\x84' \
            b'\xb5}\xe4\xf7\xf0\xa5Mz\r\x11=\xffB\xb8\x13\xfc\xd1\xf5O\x01' \
            b'\x02l1c7G\x19"\xb9\x86\xf1\x1f\x0f5\xce(&\x0e*\x9aQ\xb4\x91' \
            b'\x17XS\\\x04\xeb\x8btV\xb2\xe9\x9c0Yg\x97\xd3LA\xbf-\xb3R\x12' \
            b'\xfb|\xa0\t\xa6q\xcb{8\x10DZk\x8a\x1eu+!^\xda\xed`\x7f\x8d\xc3' \
            b'\xa3\xea\xdew\xef\xe0)\x8cn\x16i\x0b\n\xa4 \xbaC\xca\x9d~e\x93' \
            b'\x89o\x9e\x95_W\x8f\x08\xbe\xe2\xdbjp\xe6\xf8m\xcc\xe8\xcf\x9f' \
            b'\xf2?\xaf\xfd\x1d\xf3Nh\xaa\xb7\xad\x889>v\xa1\xd6;\x00\xb0' \
            b'\xe5\xbdd\xc1\xc6K,\x15y\xf9J\xd8\xab\x18\xc9\xd0\xd5P\xe7\x90' \
            b'\xae:\xa8\xbb\xe3\xc8/fa\xc2r\xdc\xf6#T[\'\x1c\x92\x83\xc0\xc4' \
            b'\x81\x98s\xec\x8546\x1a\xd2E\xbc\xa7\x14\x9b\xee\xc5\xb1\xacUx' \
            b'H\xfa\xf4\xc7%b]\x0c@\x80F\x1b\xd9\x94I\x06\xb6\xe12\x03\x99' \
            b'\x053$.\xd7'
    _decode_table = b'\xa6!"\xf9=\xfb\xf5\x06\x87Tvu\xed\x163.Z\x17P\x1c\xde' \
            b'\xafs9\xb5(\xd9\xf1\xcd\x98_-xb)\xc9\xfd\xea2\xcc1p4a\xaeM\xfe' \
            b'\xc2E$\xf8\xfc\xd7/\xd8&Y\xa0\xbd\xa5\x01\x18\xa1\x95\xeeK\x1a' \
            b'z[\xdb\xf0\'\xe6\xf4\xb2\xadJ\x14\x9a \xb96O;\xca\xe4A\x85:F\\' \
            b'\xcb<\xecc\x84f\xc4\xeb%\xaa~\xc3G\x9bt\x8b]#\x8fr\x81\x8cV' \
            b'\xc6\xd4@`\xa2m\xe5\xb0\x15XR\x0f}g\xef\xd2\x0b\xcf\r\xd6+\n' \
            b'\x9f\x80^?qh\x05\x86\xbb8\xce\x7f\xf3\x83\x03H\xd3\xfa5\xdfD|' \
            b'\x82\x93S\xa3\tjw\x13U\xdd\xbe\x00\x9c\xb4\xe3\x9e\xbc\x96\xa7' \
            b'\xe2BN7\x0e\xf6\x9d\x1b*y\xbf\xdc\xa9\x88L\xd0\xab\xc5i\xd1' \
            b'\xe1\xac\xe9\xc1\xb6{W\x90\x070\x92\xb7\x1e\xdaI\x0c\xb8\xa4' \
            b'\xff\xb3\xf2d\x8a\xc7\x02l\x08o\xf7\x89\xc0\x10\xa8\x8d\xba' \
            b'\x91Ck>\xd5e\xe0n\x12,\x94\x99\xe8\x1f\xc8\x11\x8e\xb1\xe7Q' \
            b'\x1d\x97\x04\x19'
    _key_default = (0xdfa3, 0x215f)
    _key_modifier = (0xffef, 0xff8f)
    _mhp2g_jp_hash_salt = b'S)R?Bf8xW3#5h9lGU8wR'
    _mhp2g_na_hash_salt = b'3Nc94Hq1zOLh8d62Sb69'
    _mhp3_jp_hash_salt = b'VQ(DOdIO9?X3!2GmW#XF'

    def __init__(self, game):
        """
        Initialize the cipher for the given game.

        Arguments:
        game -- Identifier of a version of Monster Hunter

        """
        self._key = [0, 0]
        # Select the salt to use when hashing
        if game == MHP2G_JP:
            self._hash_salt = self._mhp2g_jp_hash_salt
        elif game == MHP2G_NA or game == MHP2G_EU:
            self._hash_salt = self._mhp2g_na_hash_salt
        elif game == MHP3_JP:
            self._hash_salt = self._mhp3_jp_hash_salt
        else:
            raise ValueError('Invalid game selected.')

    def encrypt(self, buff):
        """
        Return an encrypted copy of the given save file data.

        Arguments:
        buff -- Data read from a decrypted save file

        """
        # Hash the unencrypted data with the salt and append it to the data
        buff += hashlib.sha1(buff[:-12] + self._hash_salt).digest()
        # Create a new seed for the XOR cipher
        seed = random.getrandbits(16)
        # Apply a substitution cipher to the data and encrypt it
        buff = DataCipher.encrypt(self, buff.translate(self._encode_table), seed)
        seed = array.array('I', [seed]).tostring()
        # Apply a substitution cipher to the XOR cipher seed and append it to the data
        return buff + seed.translate(self._encode_table).translate(self._encode_table)

    def decrypt(self, buff):
        """
        Return a decrypted copy of the given save file data.

        Arguments:
        buff -- Data read from an encrypted save file

        """
        # Get the XOR cipher seed from the end of the data and apply a
        # substitution cipher
        seed = buff[-4:].translate(self._decode_table).translate(self._decode_table)
        # Decrypted the data
        buff = DataCipher.decrypt(self, buff[:-4], array.array('I', seed)[0])
        # Apply a substitution cipher to the data
        buff = buff.translate(self._decode_table)
        # Get the hash from the end of the data
        md = buff[-20:]
        buff = buff[:-20]
        # Hash the decrypted data with the salt and compare it
        if md != hashlib.sha1(buff[:-12] + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return buff

    def encrypt_file(self, savedata_file, out_file):
        """
        Save an encrypted copy of the given save file.

        Arguments:
        savedata_file -- Path to a decrypted save file
        out_file -- Path to save the encrypted save file

        """
        with open(savedata_file, 'rb') as savedata, open(out_file, 'wb') as out:
            out.write(self.encrypt(savedata.read()))

    def decrypt_file(self, savedata_file, out_file):
        """
        Save a decrypted copy of the given save file.

        Arguments:
        savedata_file -- Path to an encrypted save file
        out_file -- Path to save the decrypted save file

        """
        with open(savedata_file, 'rb') as savedata, open(out_file, 'wb') as out:
            out.write(self.decrypt(savedata.read()))


class PSPSavedataCipher:
    """
    Cipher for Playstion Portable save files.

    This class provides encryption functions for Playstation Portable save
    files from all versions of Monster Hunter.

    Methods:
    encrypt -- Return an encrypted copy of the given PSP save file data
    decrypt -- Return a decrypted copy of the given PSP save file data
    encrypt_file -- Save an encrypted copy of the given PSP save file
    decrypt_file -- Save a decrypted copy of the given PSP save file

    """

    _hash_key_2 = b'\xfa\xaaP\xec/\xdeT\x93\xad\x14\xb2\xce\xa50\x05\xdf'
    _hash_key_3 = b'6\xa5>\xac\xc5&\x9e\xa3\x83\xd9\xec%lHHr'
    _hash_key_4 = b'\xd8\xc0\xb0\xf3>kv\x85\xfd\xfbM}E\x1e\x92\x03'
    _hash_key_5 = b'\xcb\x15\xf4\x07\xf9jR<\x04\xb9\xb2\xee\\S\xfa\x86'
    _hash_key_6 = b'pD\xa3\xae\xef]\xa5\xf2\x85\x7f\xf2\xd6\x94\xf56;'
    _hash_key_7 = b'\xecm)Y&5\xa5\x7f\x97*\r\xbc\xa3&3\x00'

    _aes_key_0C = b'\x84\x85\xc8Hu\x08C\xbc\x9b\x9a\xec\xa7\x9c\x7f`\x18'
    _aes_key_0C_sub = b'4\xe56\x9cs]\xcb\xf5\xdf\x18\x11s\xf7\xe5\xe4\x82'
    _aes_key_0E = b'\xc8q\xfd\xb3\xbc\xc5\xd2\xf2\xe2\xd7r\x9d\xdf\x82h\x82'
    _aes_key_10 = b'2)[\xd5\xea\xf7\xa3B\x16\xc8\x8eH\xffP\xd3q'
    _aes_key_10_sub = b'\xeer\xa1\xf5zE\xab[*/\xcc\xf7\x1a3v6'
    _aes_key_12 = b']\xc7\x119\xd0\x198\xbc\x02\x7f\xdd\xdc\xb0\x83}\x9d'
    _aes_key_57 = b'\x1c\x9b\xc4\x90\xe3\x06d\x81\xfaY\xfd\xb6\x00\xbb(p'
    _aes_key_64 = b'\x03\xb3\x02\xe8_\xf3\x81\xb1;\x8d\xaa*\x90\xff^a'

    _mhp_na_key = b'\x9fHl\xc2\x83\xa1\xb4\xeb\xd0\xb2<?\xe9pD\xdf'
    _mhp_jp_key = b'>\r\xb2\xef^\xa5\xbe\xef\xd6\xad\x8e\x0fn\xad\xfe\x9f'
    _mhp2_jp_key = b'\xe3\xb5\xce\xfa\xe8N\xb0\xa1\x85\x9a\xb7\x1b\xdd\xe6\xd8\xf3'
    _mhp2_na_key = b'\xb9\xa9\x00\x9do\xc2\xb4\xeb\xf4\xf8\xca\xb2\xd7r\xe9\xab'
    _mhp2g_jp_key = b'\xcd\x1f Y\xaep\xefh\xdc\xa2E\x13\xb4Z\xdb\n'
    _mhp2g_na_key = b'J\x1f\xf3Y\xae\xb6\xef\xf8\x1c\xa8\xcb#\xbc\xa5{\xb3'
    _mhp3_jp_key = b"\xe3\x05\xce\xfa\xebF\xb01\x85\x9a'[\xdf2\xd8c"

    def __init__(self, game):
        """
        Initialize the cipher for the given game.

        Arguments:
        game -- Identifier of a version of Monster Hunter

        """
        # Select the cipher key
        if game >= MHP_JP and game <= MHP_EU:
            self._hash1 = bytearray(self._hash_key_2)
            self._hash2 = self._aes_key_0C
            self._hash3 = bytearray(self._aes_key_0C_sub)
            self._cipher1 = bytearray(self._hash_key_3)
            self._cipher2 = bytearray(self._hash_key_4)
            self._cipher3 = self._aes_key_0E
            self._cipher4 = self._aes_key_57
            if game == MHP_JP or game == MHP_EU:
                self._key = bytearray(self._mhp_jp_key)
            elif game == MHP_NA:
                self._key = bytearray(self._mhp_na_key)
        elif game >= MHP2_JP and game <= MHP3_JP:
            self._hash1 = bytearray(self._hash_key_5)
            self._hash2 = self._aes_key_10
            self._hash3 = bytearray(self._aes_key_10_sub)
            self._cipher1 = bytearray(self._hash_key_6)
            self._cipher2 = bytearray(self._hash_key_7)
            self._cipher3 = self._aes_key_12
            self._cipher4 = self._aes_key_64
            if game == MHP2_JP:
                self._key = bytearray(self._mhp2_jp_key)
            elif game == MHP2_NA or game == MHP2_EU:
                self._key = bytearray(self._mhp2_na_key)
            elif game == MHP2G_JP:
                self._key = bytearray(self._mhp2g_jp_key)
            elif game == MHP2G_NA or game == MHP2G_EU:
                self._key = bytearray(self._mhp2g_na_key)
            elif game == MHP3_JP:
                self._key = bytearray(self._mhp3_jp_key)
        else:
            raise ValueError('Invalid game selected.')

    def hash(self, buff):
        """
        Return a hash of the given encrypted PSP save file data.

        Arguments:
        buff -- Data read from an encrypted PSP save file

        """
        buff = bytearray(buff)
        for i in range(16):
            buff[i-16] ^= self._hash3[i]
        aes = AES.new(self._hash2, AES.MODE_CBC, b'\x00' * 16)
        buff = bytearray(aes.encrypt(bytes(buff))[-16:])
        for i in range(16):
            buff[i] ^= self._hash1[i] ^ self._key[i]
        aes = AES.new(self._hash2, AES.MODE_CBC, b'\x00' * 16)
        return aes.encrypt(bytes(buff))

    def encrypt(self, buff):
        """
        Return an encrypted copy of the given PSP save file data.

        Arguments:
        buff -- Data read from a decrypted PSP save file

        """
        xor_key = bytearray(os.urandom(16))
        xor_buff = bytearray()
        for i in range(1, len(buff) // 16 + 1):
            xor_buff.extend(xor_key[:12])
            xor_buff.extend(array.array('I', [i]).tostring())
        aes = AES.new(self._cipher4, AES.MODE_CBC, b'\x00' * 16)
        xor_buff = bytearray(aes.decrypt(bytes(xor_buff)))
        buff = bytearray(buff)
        for i in range(len(buff)):
            buff[i] ^= xor_buff[i]
        for i in range(12):
            xor_key[i] ^= self._cipher1[i]
        aes = AES.new(self._cipher3, AES.MODE_CBC, b'\x00' * 16)
        xor_key = bytearray(aes.encrypt(bytes(xor_key)))
        for i in range(16):
            xor_key[i] ^= self._cipher2[i] ^ self._key[i]
        return bytes(xor_key) + bytes(buff)

    def decrypt(self, buff):
        """
        Return a decrypted copy of the given PSP save file data.

        Arguments:
        buff -- Data read from an encrypted PSP save file

        """
        xor_key = bytearray(buff[:16])
        for i in range(16):
            xor_key[i] ^= self._cipher2[i] ^ self._key[i]
        aes = AES.new(self._cipher3, AES.MODE_CBC, b'\x00' * 16)
        xor_key = bytearray(aes.decrypt(bytes(xor_key))[:12])
        for i in range(12):
            xor_key[i] ^= self._cipher1[i]
        xor_buff = bytearray()
        for i in range(1, len(buff) // 16):
            xor_buff.extend(xor_key)
            xor_buff.extend(array.array('I', [i]).tostring())
        aes = AES.new(self._cipher4, AES.MODE_CBC, b'\x00' * 16)
        xor_buff = bytearray(aes.decrypt(bytes(xor_buff)))
        buff = bytearray(buff[16:])
        for i in range(len(buff)):
            buff[i] ^= xor_buff[i]
        return bytes(buff)

    def encrypt_file(self, pspsavedata_file, out_file):
        """
        Save an encrypted copy of the given PSP save file and return it's hash.

        Arguments:
        pspsavedata_file -- Path to a decrypted PSP save file
        out_file -- Path to save the encrypted PSP save file

        """
        with open(pspsavedata_file, 'rb') as pspsavedata, open(out_file, 'wb') as out:
            buff = self.encrypt(pspsavedata.read())
            out.write(buff)
            return self.hash(buff)

    def decrypt_file(self, pspsavedata_file, out_file):
        """
        Save a decrypted copy of the given PSP save file and return it's hash.

        Arguments:
        pspsavedata_file -- Path to an encrypted PSP save file
        out_file -- Path to save the decrypted PSP save file

        """
        with open(pspsavedata_file, 'rb') as pspsavedata, open(out_file, 'wb') as out:
            buff = pspsavedata.read()
            out.write(self.decrypt(buff))
            return self.hash(buff)


class QuestCipher:
    """
    Cipher for Monster Hunter quest files.

    This class provides encryption functions for quest files downloaded from
    the DLC websites of the 3rd and 2nd G versions of Monster Hunter.

    Methods:
    csum -- Return the checksum of the given quest file data
    encrypt -- Return an encrypted copy of the given quest file data
    decrypt -- Return a decrypted copy of the given quest file data
    encrypt_file -- Save an encrypted copy of the given quest file and return it's checksum
    decrypt_file -- Save a decrypted copy of the given quest file and return it's checksum

    """

    _mhp2g_key_default = (0xff9d, 0xffa9, 0xffc7, 0xfff1)
    _mhp3_key_default = (0xffa9, 0xff9d, 0xfff1, 0xffc7)
    _mhp2g_key_modifier = (0x1709, 0x3df3, 0x747b, 0xb381)
    _mhp3_key_modifier = (0x3df3, 0x1709, 0xb381, 0x747b)
    _mhp2g_jp_hash_salt = b'37wyS2Jfc3x5w9oG'
    _mhp2g_na_hash_salt = b'Vd6gh8F30wA86Ex5'
    _mhp3_jp_hash_salt =b'sR2Tf4eLAj8b3TH7'

    def __init__(self, game):
        """
        Initialize the cipher for the given game.

        Arguments:
        game -- Identifier of a version of Monster Hunter

        """
        self._key = [0, 0, 0, 0]
        # Select XOR cipher parameters and the salt to use when hashing
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
        # Initialize the XOR cipher key using a seed
        self._key[num] = seed
        if self._key[num] == 0:
            self._key[num] = self._key_default[num]

    def _next_key(self, num):
        # Calculate a new XOR cipher key based on the previous key
        self._key[num] *= self._key_modifier[num]
        self._key[num] %= self._key_default[num]
        return self._key[num]

    def csum(self, buff):
        """
        Return the checksum of the given quest file data.

        Arguments:
        buff -- Data read from an encrypted quest file

        """
        return sum(bytearray(buff)) & 0xffff

    def encrypt(self, buff):
        """
        Return an encrypted copy of the given quest file data.

        Arguments:
        buff -- Data read from a decrypted quest file

        """
        size = array.array('I', [len(buff)]).tostring()
        # Hash the unencrypted data with the salt
        md = hashlib.sha1(buff + self._hash_salt).digest()
        # Add the size and hash to the start of the data
        buff = array.array('H', size + md + buff)
        # Create new seeds for the XOR cipher
        seed = []
        for i in range(4):
            seed.insert(0, random.getrandbits(16))
            self._init_key(seed[0], i)
        # Apply an XOR cipher to the data using a new key every 2 bytes
        for i in range(len(buff)):
            buff[i] ^= self._next_key(i%4)
        # Add the XOR cipher seeds to the start of the data
        for i in range(4):
            buff.insert(0, seed[i])
        return buff.tostring()

    def decrypt(self, buff):
        """
        Return a decrypted copy of the given quest file data.

        Arguments:
        buff -- Data read from an encrypted quest file

        """
        buff = array.array('H', buff)
        # Get the XOR cipher seeds from the start of the data
        for i in range(4):
            self._init_key(buff.pop(0), i)
        # Apply an XOR cipher to the data using a new key every 2 bytes
        for i in range(len(buff)):
            buff[i] ^= self._next_key(i%4)
        buff = buff.tostring()
        # Get the size from the start of the data
        size = array.array('I', buff[:4])[0]
        # Get the hash from the start of the data
        md = buff[4:24]
        buff = buff[24:]
        # Check the size to make sure it matches
        if size != len(buff):
            raise ValueError('Invalid file size in header.')
        # Hash the decrypted data with the salt and compare it
        if md != hashlib.sha1(buff + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return buff

    def encrypt_file(self, quest_file, out_file):
        """
        Save an encrypted copy of the given quest file and return it's checksum.

        Arguments:
        quest_file -- Path to a decrypted quest file
        out_file -- Path to save the encrypted quest file

        """
        with open(quest_file, 'rb') as quest, open(out_file, 'wb') as out:
            buff = self.encrypt(quest.read())
            out.write(buff)
            return self.csum(buff)

    def decrypt_file(self, quest_file, out_file):
        """
        Save a decrypted copy of the given quest file and return it's checksum.

        Arguments:
        quest_file -- Path to an encrypted quest file
        out_file -- Path to save the decrypted quest file

        """
        with open(quest_file, 'rb') as quest, open(out_file, 'wb') as out:
            buff = quest.read()
            out.write(self.decrypt(buff))
            return self.csum(buff)

class BonusCipher:
    """
    Cipher for Monster Hunter bonus files.

    This class provides encryption functions for bonus files downloaded from
    the DLC websites of the 3rd version of Monster Hunter.

    Methods:
    bits_to_buff -- Convert a bonus bit field to a byte field
    buff_to_bits -- Convert a bonus byte field to a bit field
    encrypt -- Return an encrypted copy of the given bonus file data
    decrypt -- Return a decrypted copy of the given bonus file data
    encrypt_file -- Save an encrypted copy of the given bonus file
    decrypt_file -- Save a decrypted copy of the given bonus file

    """

    _mhp3_key1 = b'd\x1e\x85b'
    _mhp3_key2 = b'\x95\x86'
    _mhp3_header = b'MHP3rd Bonus'
    _mhp3_bytemask = b'Ly\x1dV\xeb\xbc,\xea\x92\xf7\xd7s\x9b\x86\xa6\xe7\xa9K\x1f\xf4\xf3ix\x89\xc8X\xe3<5\xf8\xc3\xe9}?\xc9\x9e'

    def __init__(self, game):
        """
        Initialize the cipher for the given game.

        Arguments:
        game -- Identifier of a version of Monster Hunter

        """
        # Select keys, header and byte mask to use
        if game == MHP3_JP:
            self._key1 = self._mhp3_key1
            self._key2 = self._mhp3_key2
            self._header = self._mhp3_header
            self._bytemask = self._mhp3_bytemask
        else:
            raise ValueError('Invalid game selected.')

    def bits_to_buff(self, bits):
        """
        Convert a bonus bit field to a byte field.

        Arguments:
        bits -- Identifier of a version of Monster Hunter

        """
        buff = bytearray(len(self._bytemask))
        for i in range(len(self._bytemask)):
            if bits & 1 == 1:
                buff[i] = self._bytemask[i]
            else:
                buff[i] = self._bytemask[i] ^ 0xff
            bits >>= 1
        return bytes(buff)

    def buff_to_bits(self, buff):
        """
        Convert a bonus byte field to a bit field.

        Arguments:
        buff -- Identifier of a version of Monster Hunter

        """
        bits = 0
        for i in range(len(self._bytemask)):
            if buff[i] == self._bytemask[i]:
                bits += 1 << i
        return bits

    def encrypt(self, buff):
        """
        Return an encrypted copy of the given bonus file data.

        Arguments:
        buff -- Data read from a decrypted bonus file

        """
        if len(buff) != len(self._bytemask):
            ValueError('Invalid size.')
        buff = bytearray(buff) + struct.pack('>H', sum(buff) & 0xffff)
        for i in range(len(buff)):
            buff[i] ^= self._key2[i%2]
        buff += struct.pack('>H', sum(buff) & 0xffff)
        for i in range(len(buff)):
            buff[i] ^= self._key1[i%4]
        buff += struct.pack('>H', sum(buff) & 0xffff)
        return self._header + bytes(buff)

    def decrypt(self, buff):
        """
        Return a decrypted copy of the given bonus file data.

        Arguments:
        buff -- Data read from an encrypted bonus file

        """
        if len(buff) != (len(self._header) + len(self._bytemask) + 6):
            ValueError('Invalid size.')
        if not buff.startswith(self._header):
            ValueError('Invalid header.')
        csum = struct.unpack('>H', buff[-2:])[0]
        buff = bytearray(buff[len(self._header):-2])
        if csum != (sum(buff) & 0xffff):
            ValueError('Invalid stage 1 checksum.')
        for i in range(len(buff)):
            buff[i] ^= self._key1[i%4]
        csum = struct.unpack('>H', buff[-2:])[0]
        buff = buff[:-2]
        if csum != (sum(buff) & 0xffff):
            ValueError('Invalid stage 2 checksum.')
        for i in range(len(buff)):
            buff[i] ^= self._key2[i%2]
        csum = struct.unpack('>H', buff[-2:])[0]
        buff = buff[:-2]
        if csum != (sum(buff) & 0xffff):
            ValueError('Invalid stage 3 checksum.')
        return bytes(buff)

    def encrypt_file(self, bonus_file, out_file):
        """
        Save an encrypted copy of the given bonus file.

        Arguments:
        bonus_file -- Path to a decrypted bonus file
        out_file -- Path to save the encrypted quest file

        """
        with open(bonus_file, 'rb') as bonus, open(out_file, 'wb') as out:
            out.write(self.encrypt(bonus.read()))

    def decrypt_file(self, bonus_file, out_file):
        """
        Save a decrypted copy of the given bonus file.

        Arguments:
        bonus_file -- Path to an encrypted bonus file
        out_file -- Path to save the decrypted bonus file

        """
        with open(bonus_file, 'rb') as bonus, open(out_file, 'wb') as out:
            out.write(self.decrypt(bonus.read()))

