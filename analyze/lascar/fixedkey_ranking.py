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
            resabs = np.abs(results[0])
            res = results[0]
            # plt.plot(results)
            # plt.plot(results[1:])
            # plt.ylim([-0.1, 0.1])
            # plt.show()

            self.outcome.append((engine.finalize_step[-1], np.var(results[0]) / np.var(results[1])))
            # self.outcome.append((engine.finalize_step[-1], 1 / np.std(max - resabs)))
            # self.outcome.append((engine.finalize_step[-1], np.max(np.abs(results[0])) / np.std(results[0])))
            # self.outcome.append((engine.finalize_step[-1], np.max(np.abs(results[0]))))
            # self.outcome.append((engine.finalize_step[-1], np.std(results[1])))

    output_method = CpaOutput(engine)
    session = lascar.Session(
        trace,
        engine=engine,
        output_method=output_method,
        output_steps=list(range(1000, 200_000, 100)),
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
        output_steps=list(range(0, 200_000, 1000)),
        progressbar=False,
    )
    session.run(batch_size=100_000)
    return output_method.outcome


def main():
    _, ax = plt.subplots()
    outcomes = []
    for name, func, selector in (
        # ("subbyte cpa byte", do_cpa, jit(lambda value, key: lascar.tools.aes.sbox[value[0] ^ key])),
        ("subbyte cpa hamming", do_cpa, jit(lambda value, key: lascar.hamming(lascar.tools.aes.sbox[value[0] ^ key]))),
        # ("subbyte ttest", do_ttest, jit(lambda value, key: int(lascar.tools.aes.sbox[value[0] ^ key] & 0x01 == 0))),
        # ("addkey cpa byte", do_cpa, jit(lambda value, key: value[0] ^ key)),
        # ("addkey cpa hamming", do_cpa, jit(lambda value, key: lascar.hamming(value[0] ^ key))),
        # ("addkey ttest", do_ttest, jit(lambda value, key: int((value[0] ^ key) & 0x01 == 0))),
    ):
        for dataset in (
            # "elmohwdiff_loop5_fixedkey",
            # "elmohwpower_loop5_fixedkey",
            # "elmodiff_loop5_fixedkey",
            # "elmopower_loop5_fixedkey",
            "cw_loop5_fixedkey",
            # "cw_loop3_fixedkey",
            # "cwxmega_loop5_fixedkey",
        ):
            outcome = func(datasets.dataset(dataset)[:50_000], selector)
            outcomes.append((f"{dataset} {name}", outcome))
            ax.plot(*zip(*outcome), label=f"{dataset} {name}")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
