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
        printf("usage: %s inputfile outputpath\n", argv[0]);
        return 1;
    }
    FILE *input = fopen(argv[1], "rb");
    if (input == NULL) {
        printf("error: unable to open input file.\n");
        return 2;
    }
    unsigned int i = 17 * 2048;
    unsigned char *data = malloc(i);
    if (data == NULL) {
        printf("error: unable to malloc for table of contents.\n");
        return 3;
    }
    fread(data, 1, i, input);
    if (ferror(input)) {
        printf("error: unable to read table of contents from input file.\n");
        return 4;
    }
    data_decrypt(data, i);
    file_info toc[FILE_COUNT];
    data_parse_toc((unsigned int *)data, toc);
    free(data);
    FILE *output;
    char outputfile[256];
    for (i = 0; i < FILE_COUNT; i++) {
        fseek(input, toc[i].offset, SEEK_SET);
        data = malloc(toc[i].size);
        if (data == NULL) {
            printf("error: unable to malloc for file data.\n");
            return 5;
        }
        fread(data, 1, toc[i].size, input);
        if (ferror(input)) {
            printf("error: unable to read file data from input file.\n");
            return 6;
        }
        if (toc[i].encrypted == 1) {
            data_init_key(toc[i].offset / 2048);
            data_decrypt(data, toc[i].size);
        }
        sprintf(outputfile, "%s/%04d", argv[2], i);
        output = fopen(outputfile, "wb");
        if (output == NULL) {
            printf("error: unable to open output file.\n");
            return 7;
        }
        fwrite(data, 1, toc[i].actual_size, output);
        if (ferror(input)) {
            printf("error: unable to write file data to output file.\n");
            return 8;
        }
        free(data);
        fclose(output);
    }
    fclose(input);
    return 0;
}
