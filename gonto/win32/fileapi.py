"""Bindings for the Win32 File API."""

import sys
import ctypes
import ctypes.wintypes

# =============================================================================
# Function bindings
# =============================================================================


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.windll.LoadLibrary("kernel32.dll")
    else:
        return None

    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findfirstvolumew
    # HANDLE FindFirstVolumeW(
    #   [out] LPWSTR lpszVolumeName,
    #   [in]  DWORD  cchBufferLength
    # );
    lib.FindFirstVolumeW.argtypes = [
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
    ]
    lib.FindFirstVolumeW.restype = ctypes.wintypes.HANDLE

    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findnextvolumew
    # BOOL FindNextVolumeW(
    #   [in]  HANDLE hFindVolume,
    #   [out] LPWSTR lpszVolumeName,
    #   [in]  DWORD  cchBufferLength
    # );
    lib.FindNextVolumeW.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
    ]
    lib.FindNextVolumeW.restype = ctypes.wintypes.BOOL

    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-findvolumeclose
    # BOOL FindVolumeClose(
    #   [in] HANDLE hFindVolume
    # );
    lib.FindVolumeClose.argtypes = [
        ctypes.wintypes.HANDLE,
    ]
    lib.FindVolumeClose.restype = ctypes.wintypes.BOOL

    return lib


#: Binding of fileapi functions of ``kernel32.dll``. See source code for a list
#: of bound functions.
lib = _bind_lib()
