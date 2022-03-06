#!/usr/bin/env python
import os
import numpy as np
import lascar

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

datasets = {
    name: np.load(f"{basedir}/data/{name}.npy")
    for name in (
        "cw_plain_fixedinput",
        "cw_loop1_fixedinput",
        "cw_loop2_fixedinput",
        "cw_loop5_fixedinput",
    )
}

poi_selectors = {
    "key": lambda value: value["key"][0],
    "hw_key": lambda value: lascar.hamming(value["key"][0]),
    "addkey": lambda value: value["input"][0] ^ value["key"][0],
    "hw_addkey": lambda value: lascar.hamming(value["input"][0] ^ value["key"][0]),
    "subbytes": lambda value: lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]],
    "hw_subbytes": lambda value: lascar.hamming(lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]]),
}

poi_selector_name = "key"
poi_selector = poi_selectors[poi_selector_name]


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def _update(self, engine, result):
        self.logger.info(f"Maximum of {engine.name}:  {np.max(result):.2f}@{np.argmax(result):4d}")


def main():
    for dataname, data in datasets.items():
        trace = lascar.TraceBatchContainer(data["trace"], data)
        engine = lascar.SnrEngine(
            name=f"{poi_selector_name} for {dataname}",
            partition_function=poi_selectors[poi_selector_name],
            partition_range=range(9) if "hw" in poi_selector_name else range(256),
            jit=False,
        )

        session = lascar.Session(trace, engine=engine, output_method=MaxArgmaxOutputMethod(engine))
        session.run(batch_size=100_000)


if __name__ == "__main__":
    main()
