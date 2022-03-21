#!/usr/bin/env python
import random

import numpy as np
import scipy.signal
import lascar
from numba import njit

import datasets

lascar.logger.setLevel(lascar.logging.CRITICAL)


def cpa_multiple(dataset, selection_functions):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []
            self.name = engines[0].name

        def _update(self, engine, results):
            self.result = results[0]

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    selection_functions = {name: njit()(f) for name, f in selection_functions.items()}
    engines = [
        lascar.CpaEngine(
            name=name,
            selection_function=f,
            guess_range=range(1),
            jit=False,
        )
        for name, f in selection_functions.items()
    ]
    output_methods = [CpaOutput(engine) for engine in engines]
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_methods,
        progressbar=False,
    )
    session.run(batch_size=100_000)
    # return np.asarray(
    #     [(output_method.name, output_method.result) for output_method in output_methods],
    #     dtype=[("name", "O", 1), ("cpa", "f8", len(output_methods[0].result))],
    # )
    return [(output_method.name, output_method.result) for output_method in output_methods]


def cpa_full(dataset, selection_function, guess_range):
    class CpaOutput(lascar.OutputMethod):
        def _update(self, engine, results):
            self.result = results[0]

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=selection_function,
        guess_range=guess_range,
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


def cpa_leakage_rate(dataset, selection_function, randoms=16):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []

        def _update(self, engine, results):
            resabs = np.abs(results)
            self.result.append((engine.finalize_step[-1], -np.std(results[1:]) / np.max(resabs[0])))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=lambda value, guess: selection_function(value) if guess == 0 else random.randint(0, 1),
        guess_range=range(randoms),
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


def cpa_leakage_rates(dataset, selection_functions, randoms=16):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []
            self.name = engines[0].name

        def _update(self, engine, results):
            resabs = np.abs(results)
            self.result.append((engine.finalize_step[-1], -np.std(results[1:]) / np.max(resabs[0])))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    selection_functions = {name: njit()(f) for name, f in selection_functions.items()}

    def getf(name):
        f = selection_functions[name]

        @njit
        def func(value, guess):
            if guess == 0:
                return f(value)
            else:
                return random.randint(0, 1)

        return func

    engines = [
        lascar.CpaEngine(
            name=name,
            selection_function=getf(name),
            guess_range=range(randoms),
            jit=False,
        )
        for name, f in selection_functions.items()
    ]
    output_methods = [CpaOutput(engine) for engine in engines]
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_methods,
        output_steps=range(0, len(dataset), len(dataset) // 100),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return [(output_method.name, output_method.result) for output_method in output_methods]
