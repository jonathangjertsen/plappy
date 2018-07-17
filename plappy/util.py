"""
util module - Utilities for Plappy

Functions:
    * unique_key(key, collection): Creates a new key based on the old key which is guaranteed to be unique in the collection
    * dB(linear_gain): Convert from linear gain factor to dB
    * dBFS(linear): Convert from linear value to dBFS value
    * linear_gain(dB): Convert from dB to linear gain factor
    * linear(dBFS): Convert from dBFS to linear value
Variables:
    * linear_max: Maximum linear value
"""
import numpy as np

from plappy.plappyconfig import config

linear_max = np.iinfo(config.buffer_dtype).max

def unique_key(old_key: str, collection: dict) -> str:
    """Create a old_key which is guaranteed to be unique in the collection"""
    counter = 2
    new_key = old_key
    while new_key in collection:
        new_key = f"{old_key}{counter}"
        counter += 1
    return new_key


def dB(linear_gain: float) -> float:
    """Convert from linear gain factor to dB"""
    return 20 * np.log10(linear_gain)


def dBFS(linear: float) -> float:
    """Convert from linear value to dBFS value"""
    return dB(abs(linear) / linear_max)


def linear_gain(db: float) -> float:
    """Convert from dB to linear gain factor"""
    return 10 ** (db / 20)


def linear(dbfs: float) -> float:
    """Convert from dBFS to linear value"""
    return linear_max * linear_gain(dbfs)

