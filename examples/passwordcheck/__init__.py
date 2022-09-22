import os
import random

import numpy as np

import capture


def randints(n):
    return [random.randint(0, 255) for _ in range(n)]


def capture_passwordcheck(
    name,
    number_of_traces,
    number_of_samples,
    attempt,
    password,
):
    data = capture.capture_generic(
        name=name,
        number_of_traces=number_of_traces,
        inputfunction=lambda: attempt() + password(),
        fromfile=os.path.join(os.path.dirname(__file__), "passwordcheck.c"),
        number_of_samples=number_of_samples,
    )
    data2 = np.zeros(
        len(data),
        [
            ("trace", "f8", len(data[0]["trace"])),
            ("attempt", "u1", 5),
            ("password", "u1", 5),
        ],
    )
    data2["trace"] = data["trace"]
    data2["attempt"] = data["input"][:, :5]
    data2["password"] = data["input"][:, 5:]
    return data2


def capture_passwordcheck_neutral(
    name,
    number_of_traces,
    number_of_samples,
    attempt,
    password,
):
    data = capture.capture_generic(
        name=name,
        number_of_traces=number_of_traces,
        inputfunction=lambda: attempt() + password(),
        fromfile=os.path.join(os.path.dirname(__file__), "passwordcheck_neutral.c"),
        number_of_samples=number_of_samples,
    )
    data2 = np.zeros(
        len(data),
        [
            ("trace", "f8", len(data[0]["trace"])),
            ("attempt", "u1", 5),
            ("password", "u1", 5),
        ],
    )
    data2["trace"] = data["trace"]
    data2["attempt"] = data["input"][:, :5]
    data2["password"] = data["input"][:, 5:]
    return data2
