#!/usr/bin/env python
import random

import numpy as np
import lascar

import datasets

lascar.logger.setLevel(lascar.logging.CRITICAL)


def cpa(dataset, selection_function, correct_key):
    class CpaOutputRanking(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.ranks = []

        def _update(self, engine, results):
            maxs = np.argsort(np.max(np.abs(results), axis=1))[::-1]
            self.ranks.append((engine.finalize_step[-1], np.where(maxs == correct_key)[0][0]))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset["input"])

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=selection_function,
        guess_range=range(256),
    )
    output_method = CpaOutputRanking(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        output_steps=list(range(0, len(dataset), 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.ranks


def ttest(dataset, selection_function, correct_key):
    class TtestOutputRanking(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.ranks = []
            self.rank_data = {}

        def _update(self, engine, results):
            guess = int(engine.name.split(" ")[-1])
            step = engine.finalize_step[-1]
            if step not in self.rank_data:
                self.rank_data[step] = []
            self.rank_data[step].append((np.max(np.abs(results)), guess))

        def _finalize(self):
            for step, values in self.rank_data.items():
                vals = sorted(values, reverse=True)
                self.ranks.append((step, [v[1] for v in vals].index(correct_key)))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset["input"])

    engines = [
        lascar.TTestEngine(
            name=f"ttest {guess}",
            partition_function=selection_function(guess),
        )
        for guess in set([random.randint(0, 255) for _ in range(20)] + [correct_key])
    ]
    output_method = TtestOutputRanking(*engines)
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_method,
        output_steps=list(range(0, len(dataset), 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.ranks


def snr(dataset, selection_function, selection_range, correct_key):
    class SnrOutputRanking(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.ranks = []
            self.rank_data = {}

        def _update(self, engine, results):
            guess = int(engine.name.split(" ")[-1])
            step = engine.finalize_step[-1]
            if step not in self.rank_data:
                self.rank_data[step] = []
            self.rank_data[step].append((np.max(np.abs(results)), guess))

        def _finalize(self):
            for step, values in self.rank_data.items():
                vals = sorted(values, reverse=True)
                self.ranks.append((step, [v[1] for v in vals].index(correct_key)))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset["input"])

    engines = [
        lascar.SnrEngine(
            name=f"snr {guess}",
            partition_function=selection_function(guess),
            partition_range=selection_range,
        )
        for guess in set([random.randint(0, 255) for _ in range(20)] + [correct_key])
    ]
    output_method = SnrOutputRanking(*engines)
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_method,
        output_steps=list(range(0, len(dataset), 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.ranks
