import random

import numpy as np
import scipy.signal
import lascar
from numba import njit

lascar.logger.setLevel(lascar.logging.CRITICAL)


def cpa(dataset, selection_functions, guess_range=range(1), higherorder_rois=None):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []
            self.name = engines[0].name

        def _update(self, engine, results):
            if len(results) > 1:
                self.result = list(zip(engine._guess_range, results))
            else:
                self.result = results[0]

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)
    if higherorder_rois:
        trace.leakage_processing = lascar.CenteredProductProcessing(
            container=trace,
            rois=higherorder_rois,
            batch_size=100_000,
        )

    selection_functions = {name: njit()(f) for name, f in selection_functions.items()}
    engines = [
        lascar.CpaEngine(
            name=name,
            selection_function=f,
            guess_range=guess_range,
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
    return [(output_method.name, output_method.result) for output_method in output_methods]


def cpa_ranking(dataset, selection_function, correct_key, guess_range=range(256)):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []
            self.name = engines[0].name

        def _update(self, engine, results):
            maxs = np.argsort(np.max(np.abs(results), axis=1))[::-1]
            self.result.append((engine.finalize_step[-1], np.where(maxs == correct_key)[0][0]))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    engine = lascar.CpaEngine(
        name="cpa",
        selection_function=selection_function,
        guess_range=guess_range,
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


def cpa_leakage_rate(dataset, selection_function, randoms=16):
    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.result = []

        def _update(self, engine, results):
            resabs = np.abs(results)
            self.result.append((engine.finalize_step[-1], -np.std(results[1:]) / np.max(resabs[0])))

    trace = lascar.TraceBatchContainer(dataset["trace"], dataset)

    selection_function = njit()(selection_function)
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
