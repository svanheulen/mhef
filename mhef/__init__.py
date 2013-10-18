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

    def encrypt_file(self, data_file, out_file, exceptions=[]):
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
                if i in exceptions:
                    out.write(buff)
                else:
                    out.write(self.encrypt(buff, toc[i]))

    def decrypt_file(self, data_file, out_file, exceptions=[]):
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
                if i in exceptions:
                    out.write(buff)
                else:
                    out.write(self.decrypt(buff, toc[i]))


class SavedataCypher(DataCypher):
    def __init__(self, encode_table, decode_table, key_default, key_modifier, hash_salt):
        DataCypher.__init__(self, encode_table, decode_table, key_default, key_modifier)
        self._hash_salt = hash_salt

    def encrypt(self, buff):
        buff += hashlib.sha1(buff[:-12] + self._hash_salt).digest()
        seed = random.getrandbits(16)
        buff = DataCypher.encrypt(self, buff.translate(self._encode_table), seed)
        seed = array.array('I', [seed]).tobytes()
        return buff + seed.translate(self._encode_table).translate(self._encode_table)

    def decrypt(self, buff):
        seed = buff[-4:].translate(self._decode_table).translate(self._decode_table)
        buff = DataCypher.decrypt(self, buff[:-4], array.array('I', seed)[0])
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
            out.write(self.encrypt(quest.read()))

    def decrypt_file(self, quest_file, out_file):
        with open(quest_file, 'rb') as quest, open(out_file, 'wb') as out:
            out.write(self.decrypt(quest.read()))

