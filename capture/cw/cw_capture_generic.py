#!/usr/bin/env python
import os
import numpy as np
import tqdm

import securec
import securec.util
import jinja2

filedir = os.path.abspath(os.path.dirname(__file__))

TEMPLATE = open(os.path.join(filedir, "generic_simpleserial.j2")).read()


def _capture_single(data, cmd=0x01, samples=500):
    securec.config.scope.adc.samples = samples
    securec.config.scope.arm()
    securec.config.target.flush()
    securec.config.target.simpleserial_write(cmd, data)
    return securec.util.capture()


def _capture(
    number_of_traces,
    inputfunction,
    number_of_samples=500,
    checkoutput=None,
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

        if checkoutput and i in (0, number_of_traces - 1):
            actual_output = securec.config.target.simpleserial_read(0x01)
            expected_output = checkoutput(data["input"][i])
            if list(actual_output) != list(expected_output):
                raise Exception(f"{actual_output} != {expected_output}")
    return data


def capture(
    number_of_traces,
    inputfunction,
    code=None,
    fromfile=None,
    number_of_samples=500,
    platform="arm",
    checkoutput=None,
    **kwargs,
):
    # Generate program
    template = jinja2.Environment().from_string(TEMPLATE)
    rendered = template.render(dict(number_of_traces=number_of_traces, code=code, fromfile=fromfile))
    with open(os.path.join(filedir, "_generic_simpleserial.c"), "w") as fp:
        fp.write(rendered)

    # Setup, compile and flash
    scope, target = securec.util.init(platform="CWLITE" + platform.upper())
    securec.util.compile_and_flash(os.path.join(filedir, "_generic_simpleserial.c"))
    scope.default_setup()
    securec.util.reset_target()

    data = _capture(
        number_of_traces=number_of_traces,
        inputfunction=inputfunction,
        number_of_samples=number_of_samples,
        checkoutput=checkoutput,
    )
    securec.util.exit()
    return data
