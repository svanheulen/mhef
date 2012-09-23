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

#ifndef DATA_H
#define DATA_H

#define FILE_COUNT 5955
#define SIZE_COUNT 1289

typedef struct {
    unsigned int offset;
    unsigned int size;
    char encrypted;
} file_info;

void data_init_key(unsigned int block);
int data_decrypt(unsigned char *data, unsigned int size);
int data_encrypt(unsigned char *data, unsigned int size);
void data_parse_toc(unsigned int *data, file_info toc[]);

#endif
