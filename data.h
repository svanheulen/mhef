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
