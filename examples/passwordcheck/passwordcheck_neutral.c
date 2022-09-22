/*  -*- tab-width: 4; c-basic-offset: 4; c-file-style: "linux";
 * indent-tabs-mode: nil; -*-
 */

#include <stdbool.h>
#include <stdint.h>
#include <string.h>

uint8_t attempt[5];
uint8_t password[5];
volatile bool result;


void setup(uint8_t *input_data)
{
    memcpy(attempt, input_data, 5);
    memcpy(password, input_data + 5, 5);
}

void run(void)
{
    uint8_t res = 0;
    for (size_t i = 0; i < sizeof(password); i++)
    {
        res |= attempt[i] ^ password[i];
    }
    result = res == 0;
}

void teardown(void)
{
}
