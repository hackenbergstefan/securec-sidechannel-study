#!/usr/bin/env python
import os
import numpy as np
from securec.cpa import pearson_pointwise, hw_vec, sbox_vec

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

datasets = {
    name: np.load(f"{basedir}/data/{name}.npy")
    for name in (
        "cw_plain_fixedinput",
        "cw_loop1_fixedinput",
        "cw_loop2_fixedinput",
    )
}

poi_selectors = {
    "key": lambda data: data["key"][:, 0],
    "hw_key": lambda data: hw_vec(data["key"][:, 0]),
    "addkey": lambda data: data["input"][:, 0] ^ data["key"][:, 0],
    "hw_addkey": lambda data: hw_vec(data["input"][:, 0] ^ data["key"][:, 0]),
    "subbytes": lambda data: sbox_vec(data["input"][:, 0] ^ data["key"][:, 0]),
    "hw_subbytes": lambda data: hw_vec(sbox_vec(data["input"][:, 0] ^ data["key"][:, 0])),
}

poi_selector_name = "key"
poi_selector = poi_selectors[poi_selector_name]


def main():
    for i, (dataname, data) in enumerate(datasets.items()):
        maxpearson = np.max(np.abs(pearson_pointwise(data["trace"], poi_selector(data))))
        print(f"Max correlation on {poi_selector_name} for {dataname:20s}: {maxpearson:02f}")


if __name__ == "__main__":
    main()
