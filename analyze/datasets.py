import os
import sys

import numpy as np

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(basedir)

import capture
from capture import capture_generic, randints

capture.elmo_capture_generic.STDERR_TO_NULL = True

_cache = {}


def dataset(name, force_reload=True):
    if force_reload is False and name in _cache:
        return _cache[name]
    _cache[name] = np.load(f"{basedir}/data/{name}.npy")
    return _cache[name]
