"""
plappyconfig module - Global configuration for Plappy.

Variables:
    config (SimpleNamespace): a configuration namespace.
"""
import plappy
import numpy as np

from types import SimpleNamespace as sns

config = sns(
    buffer_size = 256,
    buffer_dtype = np.int32,
    sample_rate = 44100,
    version=plappy.__version__,
    bufstate = sns(
        empty = 0,
        filled = 1,
        ready_to_push = 2,
    ),
)
