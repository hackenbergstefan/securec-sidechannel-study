import os
import numpy as np

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

_cache = {}


def dataset(name):
    if name in _cache:
        return _cache[name]
    _cache[name] = np.load(f"{basedir}/data/{name}.npy")
    return dataset(name)
