"""Bindings for the Win32 Winbase API."""

import sys

import ctypes
import ctypes.wintypes

# =============================================================================
# Function bindings
# =============================================================================


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.WinDLL("kernel32.dll", use_last_error=True)
    else:
        return None

    # https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setvolumemountpointw
    # BOOL SetVolumeMountPointW(
    #   [in] LPCWSTR lpszVolumeMountPoint,
    #   [in] LPCWSTR lpszVolumeName
    # );
    lib.SetVolumeMountPointW.argtypes = [
        ctypes.wintypes.LPCWSTR,
        ctypes.wintypes.LPCWSTR,
    ]
    lib.SetVolumeMountPointW.restype = ctypes.wintypes.BOOL

    return lib


#: Binding of winbase functions of ``kernel32.dll``. See source code for a list
#: of bound functions.
lib = _bind_lib()
