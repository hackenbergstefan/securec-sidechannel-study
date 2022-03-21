#include "hal.h"
#include "simpleserial.h"

#include "../../src/sbox.h"

uint8_t command(uint8_t cmd, uint8_t scmd, uint8_t len, uint8_t *buf)
{
    uint8_t *key = buf;
    uint8_t *input = buf + 16;
    sbox_random_t *rand = buf + 32;
    sbox_prepare(key, rand);
    sbox_lookup(input, rand);

    return 0;
}

int main(void)
{
    platform_init();
    init_uart();
    trigger_setup();

    simpleserial_init();
    simpleserial_addcmd(0x01, sizeof(sbox_random_t) + 2 * 16, command);
    while (1)
        simpleserial_get();
}

__attribute__((always_inline)) void _trigger_high(void)
{
    trigger_high();
}

__attribute__((always_inline)) void _trigger_low(void)
{
    trigger_low();
}

#include "../../src/sbox.c"
