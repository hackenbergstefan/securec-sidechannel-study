#!/usr/bin/env python
import os
import numpy as np
import lascar

lascar.logger.setLevel(lascar.logging.CRITICAL)

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

poi_selector_name = "subbytes"

correct_key = 171


class MaxArgmaxOutputMethod(lascar.OutputMethod):
    def __init__(self, *engines, **kwargs):
        super().__init__(*engines, **kwargs)
        self.ranks = {}
        self.data = {}
        for e in engines:
            if e.__class__ not in self.data:
                self.ranks[e.__class__] = []
                self.data[e.__class__] = {}

    def _update(self, engine, result):
        if isinstance(engine, lascar.CpaEngine):
            maxs = np.argsort(np.max(np.abs(result), axis=1))[::-1]
            self.ranks[lascar.CpaEngine].append(np.where(maxs == correct_key)[0][0])
        else:
            guess = int(engine.name.split(" ")[-1])
            step = engine.finalize_step[-1]
            if step not in self.data[engine.__class__]:
                self.data[engine.__class__][step] = []
            self.data[engine.__class__][step].append((np.max(np.abs(result)), guess))

    def _finalize(self):
        for engine, data in self.data.items():
            for step, values in data.items():
                vals = sorted(values, reverse=True)
                self.ranks[engine].append([v[1] for v in vals].index(correct_key))


def do(data):
    trace = lascar.TraceBatchContainer(data["trace"], data["input"])

    def ttest_selection(guess):
        def selector(value):
            return lascar.tools.aes.sbox[value[0] ^ guess] & 0x01

        return selector

    def snr_selection(guess):
        def selector(value):
            return lascar.hamming(lascar.tools.aes.sbox[value[0] ^ guess])

        return selector

    engines_ttest = [
        lascar.TTestEngine(
            name=f"ttest {guess}",
            partition_function=ttest_selection(guess),
        )
        for guess in range(1, 255, 10)
    ]

    engines_snr = [
        lascar.SnrEngine(
            name=f"snr {guess}",
            partition_function=snr_selection(guess),
            partition_range=range(9),
        )
        for guess in range(1, 255, 10)
    ]

    engine_cpa = lascar.CpaEngine(
        name=f"cpa",
        selection_function=lambda value, guess: lascar.tools.aes.sbox[value[0] ^ guess],
        guess_range=range(256),
    )

    engines = engines_ttest + engines_snr + [engine_cpa]

    output_method = MaxArgmaxOutputMethod(*engines)
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_method,
        output_steps=[50, 100, 200, 500, 1000, 2000, 5000, 10_000, 50_000, 100_000],
        progressbar=False,
    )
    session.run(batch_size=100_000)

    for cls, ranks in output_method.ranks.items():
        print(cls.__name__, ranks)


def main():
    do(datasets["cw_loop5_fixedkey"])


if __name__ == "__main__":
    main()
