#!/usr/bin/env python
import os
import numpy as np
import securec
import securec.cpa

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

datasets = {
    name: np.load(f"{basedir}/data/{name}.npy")
    for name in (
        "cw_plain_fixedkey",
        "cw_loop1_fixedkey",
        "cw_loop2_fixedkey",
        # "cw_loop3_fixedkey",
        # "cw_loop4_fixedkey",
        "cw_loop5_fixedkey",
    )
}

poi_selector_name = "subbytes"
data = datasets["cw_loop5_fixedkey"]


def ttest(arr1, arr2):
    mean1 = np.mean(arr1, axis=0)
    mean2 = np.mean(arr2, axis=0)
    var1 = np.var(arr1, axis=0)
    var2 = np.var(arr2, axis=0)
    return (mean1 - mean2) / np.sqrt(var1 / len(arr1) + var2 / len(arr2))


def dostuff(guess):
    selection = securec.cpa.sbox_vec(data["input"][:, 0] ^ guess) & 0x01 == 0
    data1 = data["trace"][selection]
    data2 = data["trace"][np.invert(selection)]
    print(guess, np.max(np.abs(ttest(data1, data2))))


def main_multiple():
    import multiprocessing as mp

    with mp.Pool() as p:
        p.map(dostuff, range(10))


if __name__ == "__main__":
    main_multiple()
