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
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

#include <stdio.h>
#include <stdlib.h>

#include "data.h"

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
    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        printf("error: unable to open output file.\n");
        return 3;
    }
    unsigned int i = 17 * 2048;
    unsigned char *data = malloc(i);
    if (data == NULL) {
        printf("error: unable to malloc for table of contents.\n");
        return 4;
    }
    fread(data, 1, i, input);
    if (ferror(input)) {
        printf("error: unable to read table of contents from input file.\n");
        return 5;
    }
    data_decrypt(data, i);
    fwrite(data, 1, i, output);
    if (ferror(input)) {
        printf("error: unable to write table of contents to output file.\n");
        return 6;
    }
    file_info toc[FILE_COUNT];
    data_parse_toc((unsigned int *)data, toc);
    free(data);
    for (i = 0; i < FILE_COUNT; i++) {
        fseek(input, toc[i].offset, SEEK_SET);
        fseek(output, toc[i].offset, SEEK_SET);
        data = malloc(toc[i].size);
        if (data == NULL) {
            printf("error: unable to malloc for file data.\n");
            return 7;
        }
        fread(data, 1, toc[i].size, input);
        if (ferror(input)) {
            printf("error: unable to read file data from input file.\n");
            return 8;
        }
        if (toc[i].encrypted == 1) {
            data_init_key(toc[i].offset / 2048);
            data_decrypt(data, toc[i].size);
        }
        fwrite(data, 1, toc[i].actual_size, output);
        if (ferror(input)) {
            printf("error: unable to write file data to output file.\n");
            return 9;
        }
        free(data);
    }
    fclose(output);
    fclose(input);
    return 0;
}
