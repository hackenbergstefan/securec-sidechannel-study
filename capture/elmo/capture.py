#!/usr/bin/env python
import os
import struct
import glob
import random
import tqdm
import numpy as np
import subprocess


def capture(
    name,
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
    with open("plaintexts.txt", "w") as fp:
        for i in tqdm.tqdm(range(trace_nums)):
            data["key"][i, :] = keyfunc()
            data["input"][i, :] = inputfunc()
            fp.write("".join(f"{x:02x}\n" for x in np.hstack((data["key"][i, :], data["input"][i, :]))))

    subprocess.check_call(
        ["sed", "-i", f"s/#define NUMBER_OF_TRACES.*/#define NUMBER_OF_TRACES {trace_nums}/", "sbox_elmo.c"]
    )
    subprocess.check_call(["make", "clean", "all"])

    subprocess.check_call(
        ["/home/stefan/elmo/elmo", "sbox_elmo.bin"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for i in range(trace_nums):
        with open(f"output/traces/trace{i + 1:05d}.trc", "rb") as fp:
            content = fp.read()
        data["trace"][i, :] = struct.unpack(f"{len(content) // 8}d", content)

    np.save(f"../../data/{name}.npy", data)

    subprocess.check_call(["rm", "-r", "output"])

    return data


fixeddata = [0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0, 0x12, 0x34, 0x56, 0x78, 0x9A]


def main():
    capture("elmo_loop5_fixedkey", keyfunc=lambda: fixeddata, trace_samples=546, trace_nums=100_000)


if __name__ == "__main__":
    main()
