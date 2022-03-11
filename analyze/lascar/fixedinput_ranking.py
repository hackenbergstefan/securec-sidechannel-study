#!/usr/bin/env python
import random
from matplotlib.pyplot import legend
import numpy as np
import lascar
import datasets
import matplotlib.pylab as plt
import numba

lascar.logger.setLevel(lascar.logging.CRITICAL)


def jit(function):
    return numba.jit(nopython=True)(function)


def do_cpa(data, selector):
    trace = lascar.TraceBatchContainer(data["trace"], data["key"])

    engine = lascar.CpaEngine(
        name=f"cpa",
        selection_function=lambda value, guess: selector(value, True) if guess == 0 else selector(value, False),
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
    trace = lascar.TraceBatchContainer(data["trace"], data["key"])

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
            partition_function=lambda value: selector(value, True),
        ),
        lascar.TTestEngine(
            name="random",
            partition_function=lambda value: selector(value, False),
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


def main_loop():
    _, ax = plt.subplots()
    outcomes = []
    for name, func, selector in (
        ("cpa byte", do_cpa, jit(lambda value, real: value[1] if real else random.randint(0, 255))),
        (
            "cpa hamming",
            do_cpa,
            jit(lambda value, real: lascar.hamming(value[1]) if real else lascar.hamming(random.randint(0, 255))),
        ),
        # ("ttest", do_ttest, jit(lambda value, real: int(value[1] & 0x01 == 0) if real else random.randint(0, 1))),
        # ("addkey cpa byte", do_cpa, jit(lambda value, key: value[0] ^ key)),
        # ("addkey cpa hamming", do_cpa, jit(lambda value, key: lascar.hamming(value[0] ^ key))),
        # ("addkey ttest", do_ttest, jit(lambda value, key: int((value[0] ^ key) & 0x01 == 0))),
    ):
        for dataset in (
            # "cw_plain_fixedinput",
            # "cw_loop1_fixedinput",
            # "cw_loop2_fixedinput",
            # "cw_loop3_fixedinput",
            "cw_loop4_fixedinput",
            # "cwxmega_plain_fixedinput",
            # "cwxmega_loop1_fixedinput",
            # "cwxmega_loop2_fixedinput",
            # "cwxmega_loop3_fixedinput",
            "cwxmega_loop4_fixedinput",
            # "elmodiff_plain_fixedinput",
            # "elmodiff_loop1_fixedinput",
            # "elmodiff_loop2_fixedinput",
            # "elmodiff_loop3_fixedinput",
            # "elmodiff_loop4_fixedinput",
            # "elmopower_plain_fixedinput",
            # "elmopower_loop1_fixedinput",
            # "elmopower_loop2_fixedinput",
            # "elmopower_loop3_fixedinput",
            # "elmopower_loop4_fixedinput",
            # "elmohwpower_plain_fixedinput",
            # "elmohwpower_loop1_fixedinput",
            # "elmohwpower_loop2_fixedinput",
            # "elmohwpower_loop3_fixedinput",
            # "elmohwpower_loop4_fixedinput",
            # "elmohwdiff_plain_fixedinput",
            # "elmohwdiff_loop1_fixedinput",
            # "elmohwdiff_loop2_fixedinput",
            # "elmohwdiff_loop3_fixedinput",
            # "elmohwdiff_loop4_fixedinput",
        ):
            if isinstance(selector, tuple):
                outcome = func(datasets.dataset(dataset), *selector)
            else:
                outcome = func(datasets.dataset(dataset), selector)
            outcomes.append((f"{dataset} {name}", outcome))
            ax.plot(*zip(*outcome), label=f"{dataset} {name}")
    ax.legend()
    plt.show()


def main_sboxleaky():
    _, ax = plt.subplots()
    outcomes = []
    for name, func, selector in (
        ("cpa", do_cpa, jit(lambda value, real: value[1] & 0x01 if real else random.randint(0, 1))),
        ("ttest", do_ttest, jit(lambda value, real: int(value[1] & 0x01 == 0) if real else random.randint(0, 1))),
    ):
        for dataset in (
            # "cw_sbox_fixedinput",
            # "elmodiff_sbox_fixedinput",
            # "elmopower_sbox_fixedinput",
            # "elmohwdiff_sbox_fixedinput",
            # "elmohwpower_sbox_fixedinput",
            "cw_sboxleaky_fixedinput",
            # "elmodiff_sboxleaky_fixedinput",
            # "elmopower_sboxleaky_fixedinput",
            # "elmohwdiff_sboxleaky_fixedinput",
            # "elmohwpower_sboxleaky_fixedinput",
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
    main_loop()
