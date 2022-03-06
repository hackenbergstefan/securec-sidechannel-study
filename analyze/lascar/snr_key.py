#!/usr/bin/env python
import os
import numpy as np
import lascar

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
    "addkey": lambda value: value["input"][0] ^ value["key"][0],
    "hw_addkey": lambda value: lascar.hamming(value["input"][0] ^ value["key"][0]),
    "subbytes": lambda value: lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]],
    "hw_subbytes": lambda value: lascar.hamming(lascar.tools.aes.sbox[value["input"][0] ^ value["key"][0]]),
}

poi_selector_name = "subbytes"
data = datasets["cw_loop5_fixedkey"]


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def _update(self, engine, result):
        self.logger.info(f"Maximum of {engine.name}:  {np.max(result):.5f}@{np.argmax(result):4d}")


def partition_functions(guess):
    if poi_selector_name == "addkey":

        def partition(value):
            return value["input"][0] ^ guess

    elif poi_selector_name == "subbytes":

        def partition(value):
            return lascar.hamming(lascar.tools.aes.sbox[value["input"][0] ^ guess])

    return partition


def main():
    trace = lascar.TraceBatchContainer(data["trace"], data)
    engines = [
        lascar.SnrEngine(
            name=f"{poi_selector_name} for {guess}",
            partition_function=partition_functions(guess),
            partition_range=range(9),
        )
        for guess in range(160, 180)
    ]

    session = lascar.Session(trace, engines=engines, output_method=MaxArgmaxOutputMethod(*engines))
    session.run(batch_size=10_000, thread_on_update=False)


if __name__ == "__main__":
    main()
