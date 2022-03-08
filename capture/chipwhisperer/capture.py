#!/usr/bin/env python
import random
import numpy as np
import tqdm

import securec
import securec.util


def _capture(data, cmd=0x01, samples=500):
    securec.config.scope.adc.samples = samples
    securec.config.scope.arm()
    securec.config.target.simpleserial_write(cmd, data)
    return securec.util.capture()


def capture(
    trace_samples=500,
    trace_nums=100,
    inputfunc=lambda: [random.randint(0, 255) for _ in range(16)],
    keyfunc=lambda: [random.randint(0, 255) for _ in range(16)],
    randfunc=lambda: [random.randint(0, 255) for _ in range(4)],
):
    data = np.zeros(
        trace_nums,
        dtype=[
            ("trace", "f8", trace_samples),
            ("input", "u1", 16),
            ("key", "u1", 16),
            ("random", "u1", 4 + 48),
        ],
    )
    for i in tqdm.tqdm(range(trace_nums)):
        data["input"][i, :] = inputfunc()
        data["key"][i, :] = keyfunc()
        data["random"][i, :] = randfunc() + [random.randint(0, 255) for _ in range(48)]
        attempt = bytes(data["input"][i, :])
        key = bytes(data["key"][i, :])
        rand = bytes(data["random"][i, :])
        data["trace"][i, :] = _capture(key + attempt + rand, samples=trace_samples)
    return data


fixeddata = [0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0, 0x12, 0x34, 0x56, 0x78, 0x9A]


def main():
    # Setup, compile and flash
    scope, target = securec.util.init(platform="CWLITEARM")
    securec.util.compile_and_flash("./sbox_simpleserial.c")
    scope.default_setup()
    securec.util.reset_target()

    # Create output
    if not os.path.exists("../../data"):
        os.mkdir("../../data")

    def record(name):
        trace_nums, inputfunc, keyfunc, randfunc = records[name]
        print("Recording ", name)
        np.save(
            f"../../data/{name}.npy",
            capture(
                trace_nums=trace_nums,
                inputfunc=inputfunc or (lambda: [random.randint(0, 255) for _ in range(16)]),
                keyfunc=keyfunc or (lambda: [random.randint(0, 255) for _ in range(16)]),
                randfunc=randfunc,
            ),
        )

    records = {
        # fmt: off

        # Plain with fixed input
        "cw_plain_fixedinput": (10_000, lambda: fixeddata, None, lambda: 4 * [0]),
        # Plain with fixed key
        "cw_plain_fixedkey": (10_000, None, lambda: fixeddata, lambda: 4 * [0]),

        # Random loop order with 1 bit random, fixed input
        "cw_loop1_fixedinput": (10_000, lambda: fixeddata, None, lambda: [0, 0, random.randint(0, 1), 0]),
        # Random loop order with 1 bit random, fixed key
        "cw_loop1_fixedkey": (10_000, None, lambda: fixeddata, lambda: [0, 0, random.randint(0, 1), 0]),

        # Random loop order with 2 bit random, fixed input
        "cw_loop2_fixedinput": (10_000, lambda: fixeddata, None, lambda: [0, 0, random.randint(0, 3), 0]),
        # Random loop order with 2 bit random, fixed key
        "cw_loop2_fixedkey": (10_000, None, lambda: fixeddata, lambda: [0, 0, random.randint(0, 3), 0]),

        # Random loop order with 5 bit random, fixed input
        "cw_loop5_fixedinput": (100_000, lambda: fixeddata, None, lambda: [0, 0, random.randint(0, 31), 0]),
        # Random loop order with 5 bit random, fixed key
        "cw_loop5_fixedkey": (100_000, None, lambda: fixeddata, lambda: [0, 0, random.randint(0, 31), 0]),

        # Masked SBOX, fixed key
        "cw_sbox_fixedkey": (100_000, None, lambda: fixeddata, lambda: [random.randint(0, 255), random.randint(0, 255), 0, 0]),
        # Masked SBOX, fixed input
        "cw_sbox_fixedinput": (10_000, lambda: fixeddata, None, lambda: [random.randint(0, 255), random.randint(0, 255), 0, 0]),

        # Maskex SBOX, fixed input, leaky lsb
        "cw_sboxleaky_fixedinput": (10_000, lambda: fixeddata, None, lambda: [random.randint(0, 255) & 0xfe, random.randint(0, 255), 0, 0]),
        # fmt: on
    }

    record("cw_plain_fixedinput")


if __name__ == "__main__":
    import os

    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()
