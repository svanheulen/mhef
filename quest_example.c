#include <stdio.h>

#include "quest.h"

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
    unsigned char data[0x6000];
    unsigned int size = fread(data, 1, 0x6000, input);
    if (ferror(input)) {
        printf("error: unable to read input file.\n");
        return 3;
    }
    fclose(input);
    if (quest_decrypt(data, size) != 0) {
        printf("error: input file is not a valid quest file.\n");
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
