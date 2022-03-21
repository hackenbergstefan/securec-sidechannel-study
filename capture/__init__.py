import random

from .cw import cw_capture_generic
from .elmo import elmo_capture_generic


def randints(n):
    return [random.randint(0, 255) for _ in range(n)]


def capture_generic(name, *args, **kwargs):
    if name.startswith("cw"):
        return cw_capture_generic.capture(
            *args,
            **kwargs,
            platform=name.split("_")[0][2:],
        )
    else:
        return elmo_capture_generic.capture(
            name,
            *args,
            **kwargs,
        )
