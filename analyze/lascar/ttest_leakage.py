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
    )
}

poi_selectors = {
    "key": lambda value: int(value["key"][0] == 0),
    "hw_key": lambda value: int(lascar.hamming(value["key"][0]) == 0),
    "addkey": lambda value: int(value["input"][0] ^ value["key"][0] == 0),
    "hw_addkey": lambda value: int(lascar.hamming(value["input"][0] ^ value["key"][0]) == 0),
    "subbytes": lambda value: int(lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]] == 0),
    "hw_subbytes": lambda value: int(lascar.hamming(lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]]) == 0),
}

poi_selector_name = "key"
poi_selector = poi_selectors[poi_selector_name]


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def _update(self, engine, result):
        result = np.abs(result)
        self.logger.info(f"Maximum of {engine.name}:  {np.max(result):.2f}@{np.argmax(result):4d}")


def main():
    for dataname, data in datasets.items():
        trace = lascar.TraceBatchContainer(data["trace"], data)
        engine = lascar.TTestEngine(
            name=f"{poi_selector_name} for {dataname}",
            partition_function=poi_selectors[poi_selector_name],
        )

        session = lascar.Session(trace, engine=engine, output_method=MaxArgmaxOutputMethod(engine))
        session.run(batch_size=100_000)
        return


if __name__ == "__main__":
    main()
