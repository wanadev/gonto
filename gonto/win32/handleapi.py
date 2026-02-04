"""Bindings for the Win32 Handle API."""

import sys
import ctypes
import ctypes.wintypes

# =============================================================================
# Consts
# =============================================================================

#: Invalid handle value for Win32 APIs that does not use NULL (``None``) as
#: invalid value.
INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value


# =============================================================================
# Function bindings
# =============================================================================


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.windll.LoadLibrary("kernel32.dll")
    else:
        return None

    # https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle
    # BOOL CloseHandle(
    #   [in] HANDLE hObject
    # );
    lib.CloseHandle.argtypes = [
        ctypes.wintypes.HANDLE,
    ]
    lib.CloseHandle.restype = ctypes.wintypes.BOOL

    return lib


#: Binding of ``kernel32.dll``. See source code for a list of bound functions.
lib = _bind_lib()
