#!/usr/bin/env python
import random
import numpy as np
import tqdm

import securec
import securec.util


random_length = 4 + 48


def _capture(data, cmd=0x01, samples=500):
    securec.config.scope.adc.samples = samples
    securec.config.scope.arm()
    securec.config.target.simpleserial_write(cmd, data)
    return securec.util.capture()


def capture(
    trace_samples=1500,
    trace_nums=100,
    randfunc=lambda: bytes([random.randint(0, 255) for _ in range(4 + 48)])
):
    data = np.zeros(trace_nums, dtype=[
        ('trace', 'f8', trace_samples),
        ('input', 'u1', 16),
        ('key', 'u1', 16),
        ('random', 'u1', 4 + 48),
    ])
    for i in tqdm.tqdm(range(trace_nums)):
        data['input'][i, :] = [random.randint(0, 255) for _ in range(16)]
        data['key'][i, :] = [random.randint(0, 255) for _ in range(16)]
        attempt = bytes(data['input'][i, :])
        key = bytes(data['key'][i, :])
        data['trace'][i, :] = _capture(key + attempt + randfunc(), samples=trace_samples)
    return data


def main():
    scope, target = securec.util.init(platform='CWLITEXMEGA')
    securec.util.compile_and_flash('./sbox_simpleserial.c')
    scope.default_setup()
    securec.util.reset_target()

    # Plain lookup
    # np.save('../../data/cw_plain.npy', capture(
    #     trace_nums=5000,
    #     randfunc=lambda: 4 * b'\x00' + bytes([random.randint(0, 255) for _ in range(48)]),

    # ))
    # np.save('../../data/cw_loop_order_1.npy', capture(
    #     trace_nums=5000,
    #     randfunc=lambda: 2 * b'\x00' + bytes([random.randint(0, 1)]) + bytes([random.randint(0, 255) for _ in range(1 + 48)]),
    # ))
    # np.save('../../data/cw_loop_order_2.npy', capture(
    #     trace_nums=5000,
    #     randfunc=lambda: 2 * b'\x00' + bytes([random.randint(0, 3)]) + bytes([random.randint(0, 255) for _ in range(1 + 48)]),
    # ))

    np.save('../../data/cw_loop_order.npy', capture(
        trace_nums=500,
        randfunc=lambda: 2 * b'\x00' + bytes([random.randint(0, 255)]) + bytes([random.randint(0, 255) for _ in range(1 + 48)]),
    ))
    # np.save('../../data/cw_sbox_in.npy', capture(
    #     trace_nums=10000,
    #     randfunc=lambda: bytes([random.randint(0, 255)]) + 3 * b'\x00' + bytes([random.randint(0, 255) for _ in range(48)]),
    # ))


if __name__ == '__main__':
    import os
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()
