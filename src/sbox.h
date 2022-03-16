#ifndef SBOX_H
#define SBOX_H

#include <stdint.h>

typedef struct
{
    uint8_t sbox_mask_in;
    uint8_t sbox_mask_out;
    uint8_t random_loop_order;
    uint8_t rfu;
    uint8_t random_preload_1[32];
    uint8_t random_preload_2[32];
    uint8_t random_preload_3[32];
} sbox_random_t;

extern uint8_t masked_sbox[256];
extern uint8_t masked_key[32];
extern uint8_t working_state[32];


void sbox_prepare(uint8_t key[16], sbox_random_t *rand);
void sbox_lookup(uint8_t input[16], sbox_random_t *rand);

void _trigger_high(void);
void _trigger_low(void);

#endif
