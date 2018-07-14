"""
util module - Utilities for Plappy

Functions:
    * unique_key(key, collection): Creates a new key based on the old key which is guaranteed to be unique in the collection
"""


def unique_key(old_key: str, collection: dict) -> str:
    """Create a old_key which is guaranteed to be unique in the collection"""
    counter = 2
    new_key = old_key
    while new_key in collection:
        new_key = f"{old_key}{counter}"
        counter += 1
    return new_key
