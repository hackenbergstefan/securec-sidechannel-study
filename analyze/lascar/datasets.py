import os
import numpy as np

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def dataset(name):
    return np.load(f"{basedir}/data/{name}.npy")
