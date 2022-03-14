#!/usr/bin/env python
import random

import numpy as np
import scipy.signal
import lascar

import datasets

lascar.logger.setLevel(lascar.logging.CRITICAL)


def cpa_full(dataset, selection_function=None):
    class CpaOutput(lascar.OutputMethod):
        def _update(self, engine, results):
            self.result = results[0]

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=selection_function or (lambda value, guess: value["key"][1]),
        guess_range=range(1),
    )
    output_method = CpaOutput(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.result


def ttest_full(dataset, selection_function=None):
    class TtestOutput(lascar.OutputMethod):
        def _update(self, engine, results):
            self.result = results

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.TTestEngine(
        name=f"cpa",
        partition_function=selection_function or (lambda value: value["key"][1] & 0x01),
    )
    output_method = TtestOutput(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.result


def cpa_leakage_metric(dataset, selection_function=None):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []

        def _update(self, engine, results):
            resabs = np.abs(results[0])
            resabs /= np.max(resabs)
            peaks, _ = scipy.signal.find_peaks(resabs, distance=10, height=0.6)
            self.result.append((engine.finalize_step[-1], -len(peaks)))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=selection_function or (lambda value, guess: value["key"][1]),
        guess_range=range(1),
    )
    output_method = CpaOutput(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        output_steps=range(0, len(dataset), 100),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.result
