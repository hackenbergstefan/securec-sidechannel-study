import os
import random

import numpy as np

import capture

fixeddata = [0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0, 0x12, 0x34, 0x56, 0x78, 0x9A]

randfuncs = {
    "plain": lambda: 4 * [0] + randints(3 * 32),
    "loop1": lambda: [random.randint(0, 1)] + 3 * [0] + randints(3 * 32),
    "loop2": lambda: [random.randint(0, 3)] + 3 * [0] + randints(3 * 32),
    "loop3": lambda: [random.randint(0, 7)] + 3 * [0] + randints(3 * 32),
    "loop4": lambda: [random.randint(0, 15)] + 3 * [0] + randints(3 * 32),
    "loop5": lambda: [random.randint(0, 31)] + 3 * [0] + randints(3 * 32),
}


def randints(n):
    return [random.randint(0, 255) for _ in range(n)]


def capture_sbox(
    name,
    number_of_traces,
    keyfunc=lambda: randints(16),
    inputfunc=lambda: randints(16),
    randfunc=lambda: randints(4 + 3 * 32),
):
    data = capture.capture_generic(
        name=name,
        number_of_traces=number_of_traces,
        inputfunction=lambda: keyfunc() + inputfunc() + randfunc(),
        fromfile=os.path.join(os.path.dirname(__file__), "sbox.c"),
    )
    data2 = np.zeros(
        len(data),
        [
            ("trace", "f8", len(data[0]["trace"])),
            ("key", "u1", 16),
            ("input", "u1", 16),
            ("random", "u1", 4 + 3 * 32),
        ],
    )
    data2["trace"] = data["trace"]
    data2["key"] = data["input"][:, :16]
    data2["input"] = data["input"][:, 16:32]
    data2["random"] = data["input"][:, 32:]
    return data2


def capture_fixedkey(name, security_level="plain", number_of_traces=1_000):
    return capture_sbox(
        name=name,
        number_of_traces=number_of_traces,
        keyfunc=lambda: fixeddata,
        randfunc=randfuncs[security_level],
    )


def capture_randomkey_randominput(name, security_level="plain", number_of_traces=1_000):
    return capture_sbox(
        name=name,
        number_of_traces=number_of_traces,
        randfunc=randfuncs[security_level],
    )
