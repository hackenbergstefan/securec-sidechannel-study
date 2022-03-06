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
        # "cw_loop3_fixedkey",
        # "cw_loop4_fixedkey",
        "cw_loop5_fixedkey",
    )
}

poi_selector_name = "subbytes"
data = datasets["cw_loop5_fixedkey"]


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def _update(self, engine, result):
        result = np.abs(result)
        self.logger.info(f"Maximum of {engine.name}:  {np.max(result):.2f}@{np.argmax(result):4d}")


def selection_functions(guess):
    if poi_selector_name == "addkey":

        def selector(value):
            return (value["input"][0] ^ guess) & 0x01

    elif poi_selector_name == "subbytes":

        def selector(value):
            return lascar.tools.aes.sbox[value["input"][0] ^ guess] & 0x01

    return selector


def main_multiple_engines():
    engines = [
        lascar.TTestEngine(
            name=f"{poi_selector_name} for {guess}",
            partition_function=selection_functions(guess),
        )
        for guess in range(160, 180)
    ]

    trace = lascar.TraceBatchContainer(data["trace"], data)
    session = lascar.Session(trace, engines=engines, output_method=MaxArgmaxOutputMethod(*engines), progressbar=True)
    session.run(batch_size=10_000, thread_on_update=True)


def main_single_engine():
    engine = lascar.TTestEngine(
        name=f"{poi_selector_name} for 171",
        partition_function=selection_functions(171),
    )

    trace = lascar.TraceBatchContainer(data["trace"], data)
    session = lascar.Session(trace, engine=engine, output_method=MaxArgmaxOutputMethod(engine), progressbar=True)
    session.run(batch_size=10_000, thread_on_update=True)


if __name__ == "__main__":
    main_multiple_engines()
