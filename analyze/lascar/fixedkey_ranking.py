#!/usr/bin/env python
import random
from matplotlib.pyplot import legend
import numpy as np
import lascar
import datasets
import matplotlib.pylab as plt
import numba

lascar.logger.setLevel(lascar.logging.CRITICAL)

correct_key = 171
wrong_key = 172


def jit(function):
    return numba.jit(nopython=True)(function)


def do_cpa(data, selector):
    trace = lascar.TraceBatchContainer(data["trace"], data["input"])

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=lambda value, guess: selector(value, correct_key)
        if guess == 0
        else selector(value, wrong_key),
        guess_range=range(2),
    )

    class CpaOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.outcome = []

        def _update(self, engine: lascar.Engine, results):
            self.outcome.append((engine.finalize_step[-1], np.max(np.abs(results[0])) / np.std(results[1])))

    output_method = CpaOutput(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        output_steps=list(range(0, 200_000, 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.outcome


def do_ttest(data, selector):
    trace = lascar.TraceBatchContainer(data["trace"], data["input"])

    class TtestOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.outcome = []
            self.tmp = None

        def _update(self, engine: lascar.Engine, results):
            if engine.name == "key":
                self.tmp = np.max(np.abs(results))
            else:
                self.outcome.append((engine.finalize_step[-1], self.tmp / np.std(results)))

    engines = [
        lascar.TTestEngine(
            name="key",
            partition_function=lambda value: selector(value, correct_key),
        ),
        lascar.TTestEngine(
            name="random",
            partition_function=lambda value: selector(value, wrong_key),
        ),
    ]

    output_method = TtestOutput(*engines)
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_method,
        output_steps=list(range(0, 200_000, 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.outcome


def do_snr(data, selector, selector_range):
    trace = lascar.TraceBatchContainer(data["trace"], data["input"])

    class SnrOutput(lascar.OutputMethod):
        def __init__(self, *engines):
            super().__init__(*engines)
            self.outcome = []
            self.tmp = None

        def _update(self, engine: lascar.Engine, results):
            if engine.name == "key":
                self.tmp = np.max(np.abs(results))
            else:
                self.outcome.append((engine.finalize_step[-1], self.tmp / np.std(results)))

    engines = [
        lascar.SnrEngine(
            name="key",
            partition_function=lambda value: selector(value, correct_key),
            partition_range=selector_range,
        ),
        lascar.SnrEngine(
            name="random",
            partition_function=lambda value: selector(value, wrong_key),
            partition_range=selector_range,
        ),
    ]

    output_method = SnrOutput(*engines)
    session = lascar.Session(
        trace,
        engines=engines,
        output_method=output_method,
        output_steps=list(range(0, 200_000, 100)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.outcome


def main():
    _, ax = plt.subplots()
    outcomes = []
    for name, func, selector in (
        ("subbyte cpa byte", do_cpa, jit(lambda value, key: lascar.tools.aes.sbox[value[0] ^ key])),
        ("subbyte cpa hamming", do_cpa, jit(lambda value, key: lascar.hamming(lascar.tools.aes.sbox[value[0] ^ key]))),
        ("subbyte ttest", do_ttest, jit(lambda value, key: int(lascar.tools.aes.sbox[value[0] ^ key] & 0x01 == 0))),
        # ("addkey cpa byte", do_cpa, jit(lambda value, key: value[0] ^ key)),
        # ("addkey cpa hamming", do_cpa, jit(lambda value, key: lascar.hamming(value[0] ^ key))),
        # ("addkey ttest", do_ttest, jit(lambda value, key: int((value[0] ^ key) & 0x01 == 0))),
    ):
        for dataset in (
            "elmohwdiff_loop5_fixedkey",
            "elmohwpower_loop5_fixedkey",
            "elmodiff_loop5_fixedkey",
            "elmopower_loop5_fixedkey",
            "cw_loop5_fixedkey",
        ):
            if isinstance(selector, tuple):
                outcome = func(datasets.dataset(dataset), *selector)
            else:
                outcome = func(datasets.dataset(dataset), selector)
            outcomes.append((f"{dataset} {name}", outcome))
            ax.plot(*zip(*outcome), label=f"{dataset} {name}")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
