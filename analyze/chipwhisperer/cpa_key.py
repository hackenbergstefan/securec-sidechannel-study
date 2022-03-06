#!/usr/bin/env python
import os
import numpy as np
from securec.cpa import pearson_pointwise, hw_vec, sbox_vec

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

datasets = {
    name: np.load(f"{basedir}/data/{name}.npy")
    for name in (
        "cw_plain_fixedkey",
        "cw_loop1_fixedkey",
        "cw_loop2_fixedkey",
        "cw_loop5_fixedkey",
    )
}

poi_selectors = {
    "addkey": lambda data: data["input"][:, 0] ^ data["key"][:, 0],
    "hw_addkey": lambda data: hw_vec(data["input"][:, 0] ^ data["key"][:, 0]),
    "subbytes": lambda data: sbox_vec(data["input"][:, 0] ^ data["key"][:, 0]),
    "hw_subbytes": lambda data: hw_vec(sbox_vec(data["input"][:, 0] ^ data["key"][:, 0])),
}

poi_selector_name = "subbytes"
poi_selector = poi_selectors[poi_selector_name]
data = datasets["cw_loop5_fixedkey"]


def main():
    maxpearson = np.max(np.abs(pearson_pointwise(data["trace"], poi_selector(data))))
    print(f"Max correlation on {poi_selector_name}: {maxpearson:02f}")


if __name__ == "__main__":
    main()
