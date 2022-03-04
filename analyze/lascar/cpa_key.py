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
    )
}

poi_selectors = {
    "addkey": lambda value, guess: value[0] ^ guess,
    "hw_addkey": lambda value, guess: lascar.hamming(value[0] ^ guess),
    "subbytes": lambda value, guess: lascar.tools.aes.sbox[value[0] ^ guess],
    "hw_subbytes": lambda value, guess: lascar.hamming(lascar.tools.aes.sbox[value[0] ^ guess]),
}

poi_selector_name = "subbytes"
poi_selector = poi_selectors[poi_selector_name]


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def _update(self, engine, result):
        maxs = np.max(np.abs(result), axis=1)
        self.logger.info(f"Maximum of {engine.name}:  {np.max(maxs):.2f} @ guess {np.argmax(maxs):4d}")


def main():
    for dataname, data in datasets.items():
        trace = lascar.TraceBatchContainer(data["trace"], data["input"])
        engine = lascar.CpaEngine(
            name=f"{poi_selector_name} for {dataname}",
            selection_function=poi_selectors[poi_selector_name],
            guess_range=range(256),
        )

        session = lascar.Session(trace, engine=engine, output_method=MaxArgmaxOutputMethod(engine))
        session.run(batch_size=100_000)


if __name__ == "__main__":
    main()
