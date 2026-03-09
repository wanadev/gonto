from typing import Any


def dict_merge(dest: dict[Any, Any], other: dict[Any, Any]) -> None:
    """Deep merge of ``"other"`` dict in ``"dest"`` dict.

    :param dest: Destination dict.
    :param other: Other dict to merge into ``dest``.

    >>> d1 = {"a": 1, "b": {"c": 3}, "d": 4, "f": 5}
    >>> d2 = {"b": {"e": 10}, "d": 14, "f": {"f": 15}}
    >>> dict_merge(d1, d2)
    >>> d1
    {'a': 1, 'b': {'c': 3, 'e': 10}, 'd': 14, 'f': {'f': 15}}
    >>> d2
    {'b': {'e': 10}, 'd': 14, 'f': {'f': 15}}
    """
    for key, value in other.items():
        if isinstance(value, dict):
            if key not in dest or not isinstance(dest[key], dict):
                dest[key] = {}
            dict_merge(dest[key], value)
        else:
            dest[key] = value
