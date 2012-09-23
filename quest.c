/*

Copyright 2012 Seth VanHeulen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

*/

#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <openssl/sha.h>

#include "quest.h"

// Default keys retrieved from game.
static const unsigned int default_key[] = {0xFFA9, 0xFF9D, 0xFFF1, 0xFFC7};
// Update keys retrieved from game.
static const unsigned int update_key[] = {0x3DF3, 0x1709, 0xB381, 0x747B};
// SHA1 hash salt retrieved from game.
static const char salt[] = "sR2Tf4eLAj8b3TH7";

int quest_decrypt(char *data, int size) {
    // Check that there is at least enough data for a header.
    if (size < 32)
        return -1;
    // Get keys from the header or a default value if they're zero.
    unsigned short key[4];
    int pos;
    for (pos = 0; pos < 4; pos++) {
        key[pos] = ((unsigned short *) data)[pos];
        if (key[pos] == 0)
            key[pos] = default_key[pos];
    }
    // Process each two byte block of the file excluding the keys.
    for (pos = 4; pos < (size / 2); pos++) {
        // Determine the key to use for this block.
        int i = pos % 4;
        // Generate the next key for this block.
        key[i] = (key[i] * update_key[i]) % default_key[i];
        // XOR this block with the new key.
        ((unsigned short *) data)[pos] ^= key[i];
    }
    // Check that the size from the header matches the data size.
    if ((size - 32) != ((int *) data)[2])
        return -1;
    // Hash the data, excluding the header and including the salt.
    char md[20];
    SHA_CTX c;
    SHA1_Init(&c);
    SHA1_Update(&c, data + 32, size - 32);
    SHA1_Update(&c, salt, 16);
    SHA1_Final(md, &c);
    // Check that the hash matches the one in the header.
    return memcmp(md, data + 12, 20);
}

int quest_encrypt(char *data, int size) {
    // Check that there is at least enough room for the header.
    if (size < 32)
        return -1;
    // Generate some random keys and copy them to the header.
    unsigned short key[4];
    srand(time(NULL));
    key[0] = rand();
    key[1] = rand();
    key[2] = rand();
    key[3] = rand();
    memcpy(data, (char *) key, 8);
    // Set the keys to a default value if they are zero.
    int pos;
    for (pos = 0; pos < 4; pos++) {
        if (key[pos] == 0)
            key[pos] = default_key[pos];
    }
    // Add the data size to the header.
    ((int *) data)[2] = size - 32;
    // Hash the data, excluding the header and including the salt.
    SHA_CTX c;
    SHA1_Init(&c);
    SHA1_Update(&c, data + 32, size - 32);
    SHA1_Update(&c, salt, 16);
    // Copy the hash to the header.
    SHA1_Final(data + 12, &c);
    // Process each two byte block of the data excluding the keys.
    for (pos = 4; pos < (size / 2); pos++) {
        // Determine the key to use for this block.
        int i = pos % 4;
        // Generate the next key for this block.
        key[i] = (key[i] * update_key[i]) % default_key[i];
        // XOR this block with the new key.
        ((unsigned short *) data)[pos] ^= key[i];
    }
    return 0;
}
