import sys

if sys.platform == "win32":
    import winreg
else:
    winreg = None
from typing import Any


def set_winreg_value(
    root: str,
    path: str | None,
    name: str,
    type_: str,
    data: Any,
) -> None:
    """Creates a Windows registry key and value and set it to the given data.

    :param root: Name of one of the ``HKEY_*`` constant (e.g.
        ``"HKEY_LOCAL_MACHINE"``).

        See: https://docs.python.org/3/library/winreg.html#hkey-constants
    :param path: The path of the subkey (e.g. ``"SOFTWARE\\\\Foobar"``).
    :param name: The name of the value (e.g. ``"MyValue"``).
    :param type_: The type of the value (e.g. ``"REG_SZ"``, ``"REG_DWORD"``).

        See: https://docs.python.org/3/library/winreg.html#value-types
    :param data: The data to put in the value.

    :raise ValueError: if an invalid root or type is provided.
    :raise WindowsError|OSError: if an error occurs when creating the key or
        the value.
    """
    if not root.startswith("HKEY_") or not hasattr(winreg, root):
        raise ValueError("Invalid root key: %s" % root)

    root_const = getattr(winreg, root)

    if not type_.startswith("REG_") or not hasattr(winreg, type_):
        raise ValueError("Invalid value type: %s" % type_)

    type_const = getattr(winreg, type_)

    with winreg.CreateKey(root_const, path) as key:  # type: ignore
        winreg.SetValueEx(key, name, 0, type_const, data)  # type: ignore
