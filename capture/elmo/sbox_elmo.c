#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "../../src/sbox.h"
#include "elmoasmfunctionsdef.h"

#define NUMBER_OF_TRACES 20000

void read_input(uint8_t *buffer, size_t length)
{
    for (size_t i = 0; i < length; i++)
    {
        readbyte(&buffer[i]);
    }
}

void read_random(uint8_t *buffer, size_t length)
{
    for (size_t i = 0; i < length; i++)
    {
        randbyte(&buffer[i]);
    }
}

int main(void)
{
    uint8_t key[16];
    uint8_t plaintext[16];
    sbox_random_t rand;
    for (uint_fast32_t i = 0; i < NUMBER_OF_TRACES; i++)
    {
        read_input(key, sizeof(key));
        read_input(plaintext, sizeof(key));
        memset(&rand, 0, sizeof(rand));
        read_random((uint8_t *)&rand, sizeof(rand));

        randbyte(&rand.random_loop_order);
        rand.random_loop_order &= 0x1F;

        rand.sbox_mask_in = 0;
        rand.sbox_mask_out = 0;

        sbox_prepare(key, &rand);
        sbox_lookup(plaintext, &rand);
    }

    endprogram();
}

__attribute__((always_inline)) void _trigger_high(void)
{
    starttrigger();
}

__attribute__((always_inline)) void _trigger_low(void)
{
    endtrigger();
}

#include "../../src/sbox.c"
