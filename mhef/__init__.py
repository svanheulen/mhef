import array
import hashlib
import os
import random


class DataCypher:
    def __init__(self, encode_table, decode_table, key_default, key_modifier):
        self._key = [0, 0]
        self._encode_table = encode_table
        self._decode_table = decode_table
        self._key_default = key_default
        self._key_modifier = key_modifier

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

    def encrypt(self, data, lba):
        data = array.array('I', data)
        self._init_key(lba)
        for i in range(len(data)):
            data[i] ^= self._next_key()
        return data.tostring().translate(self._encode_table)

    def decrypt(self, data, lba):
        data = array.array('I', data.translate(self._decode_table))
        self._init_key(lba)
        for i in range(len(data)):
            data[i] ^= self._next_key()
        return data.tostring()

    def encrypt_file(self, data_bin_dile, out_file, exceptions=[]):
        with open(data_bin_file, 'rb') as data_bin, open(out_file, 'wb') as out:
            toc_size = array.array('I', data_bin.read(4))[0] * 2048
            file_size = data_bin.seek(0, os.SEEK_END)
            data_bin.seek(0)
            toc = data_bin.read(toc_size)
            out.write(self.encrypt(toc, 0))
            toc = array.array('I', toc)
            file_count = toc.index(file_size // 2048)
            for i in range(file_count):
                data_bin.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                data = data_bin.read((toc[i+1] - toc[i]) * 2048)
                if i in exceptions:
                    out.write(data)
                else:
                    out.write(self.encrypt(data, toc[i]))

    def decrypt_file(self, data_bin_file, out_file, exceptions=[]):
        with open(data_bin_file, 'rb') as data_bin, open(out_file, 'wb') as out:
            toc_size = self.decrypt(data_bin.read(4), 0)
            toc_size = array.array('I', toc_size)[0] * 2048
            file_size = data_bin.seek(0, os.SEEK_END)
            data_bin.seek(0)
            toc = self.decrypt(data_bin.read(toc_size), 0)
            out.write(toc)
            toc = array.array('I', toc)
            file_count = toc.index(file_size // 2048)
            for i in range(file_count):
                data_bin.seek(toc[i] * 2048)
                out.seek(toc[i] * 2048)
                data = data_bin.read((toc[i+1] - toc[i]) * 2048)
                if i in exceptions:
                    out.write(data)
                else:
                    out.write(self.decrypt(data, toc[i]))


class SavedataCypher(DataCypher):
    def __init__(self, encode_table, decode_table, key_default, key_modifier, hash_salt):
        DataCypher.__init__(self, encode_table, decode_table, key_default, key_modifier)
        self._hash_salt = hash_salt

    def encrypt(self, data):
        data += hashlib.sha1(data[:-12] + self._hash_salt).digest()
        seed = random.getrandbits(16)
        data = DataCypher.encrypt(self, data.translate(self._encode_table), seed)
        seed = array.array('I', [seed]).tostring()
        return data + seed.translate(self._encode_table).translate(self._encode_table)

    def decrypt(self, data):
        seed = data[-4:].translate(self._decode_table).translate(self._decode_table)
        data = DataCypher.decrypt(self, data[:-4], array.array('I', seed)[0])
        data = data.translate(self._decode_table)
        md = data[-20:]
        data = data[:-20]
        if md != hashlib.sha1(data[:-12] + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return data


class QuestCypher:
    def __init__(self, key_default, key_modifier, hash_salt):
        self._key = [0, 0, 0, 0]
        self._key_default = key_default
        self._key_modifier = key_modifier
        self._hash_salt = hash_salt

    def _init_key(self, seed, num):
        self._key[num] = seed
        if self._key[num] == 0:
            self._key[num] = self._key_default[num]

    def _next_key(self, num):
        self._key[num] *= self._key_modifier[num]
        self._key[num] %= self._key_default[num]
        return self._key[num]

    def encrypt(self, data):
        data = array.array('I', [len(data)]).tostring() + hashlib.sha1(data + self._hash_salt).digest() + data
        data = array.array('H', data)
        seed = []
        for i in range(4):
            seed.insert(0, random.getrandbits(16))
            self._init_key(seed[0], i)
        for i in range(len(data)):
            data[i] ^= self._next_key(i%4)
        for i in range(4):
            data.insert(0, seed[i])
        return data.tostring()

    def decrypt(self, data):
        data = array.array('H', data)
        for i in range(4):
            self._init_key(data.pop(0), i)
        for i in range(len(data)):
            data[i] ^= self._next_key(i%4)
        data = data.tostring()
        size = array.array('I', data[:4])[0]
        md = data[4:24]
        data = data[24:]
        if size != len(data):
            raise ValueError('Invalid file size in header.')
        if md != hashlib.sha1(data + self._hash_salt).digest():
            raise ValueError('Invalid SHA1 hash in header.')
        return data

