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

#include <stdio.h>

#include "savedata.h"

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("usage: %s inputfile outputfile\n", argv[0]);
        return 1;
    }
    FILE *input = fopen(argv[1], "rb");
    if (input == NULL) {
        printf("error: unable to open input file.\n");
        return 2;
    }
    unsigned char data[0x259000];
    unsigned int size = fread(data, 1, 0x259000, input);
    if (ferror(input)) {
        printf("error: unable to read input file.\n");
        return 3;
    }
    fclose(input);
    if (savedata_decrypt(data, size) != 0) {
        printf("error: input file is not a valid savedata file.\n");
        return 4;
    }
    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        printf("error: unable to open output file.\n");
        return 5;
    }
    fwrite(data, 1, size, output);
    fclose(output);
    return 0;
}
