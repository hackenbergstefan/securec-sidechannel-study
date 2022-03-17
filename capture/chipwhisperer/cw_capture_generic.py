#!/usr/bin/env python
import os
import numpy as np
import tqdm

import securec
import securec.util
import jinja2

dir = os.path.abspath(os.path.dirname(__file__))

TEMPLATE = open(os.path.join(dir, "generic_simpleserial.j2")).read()


def _capture_single(data, cmd=0x01, samples=500):
    securec.config.scope.adc.samples = samples
    securec.config.scope.arm()
    securec.config.target.simpleserial_write(cmd, data)
    return securec.util.capture()


def _capture(
    number_of_traces,
    inputfunction,
    number_of_samples=500,
):
    data = np.zeros(
        number_of_traces,
        dtype=[
            ("trace", "f8", number_of_samples),
            ("input", "u1", len(inputfunction())),
        ],
    )
    for i in tqdm.tqdm(range(number_of_traces)):
        data["input"][i, :] = inputfunction()
        data["trace"][i, :] = _capture_single(bytes(data["input"][i, :]), samples=number_of_samples)
    return data


def capture(
    number_of_traces,
    inputfunction,
    code,
    number_of_samples=500,
    platform="arm",
):
    # Generate program
    template = jinja2.Environment().from_string(TEMPLATE)
    rendered = template.render(dict(number_of_traces=number_of_traces, code=code))
    with open(os.path.join(dir, "_generic_simpleserial.c"), "w") as fp:
        fp.write(rendered)

    # Setup, compile and flash
    scope, target = securec.util.init(platform="CWLITE" + platform.upper())
    securec.util.compile_and_flash(os.path.join(dir, "_generic_simpleserial.c"))
    scope.default_setup()
    securec.util.reset_target()

    return _capture(
        number_of_traces=number_of_traces,
        inputfunction=inputfunction,
        number_of_samples=number_of_samples,
    )
