#ifndef SBOX_H
#define SBOX_H

#include <stdint.h>

typedef struct
{
    uint8_t key[16];
    uint8_t input[16];

    uint8_t random_loop_order;
    uint8_t sbox_mask_in;
    uint8_t sbox_mask_out;
    uint8_t rfu;
    uint8_t random_preload_1[32];
    uint8_t random_preload_2[32];
    uint8_t random_preload_3[32];
} sbox_data_t;


#endif
