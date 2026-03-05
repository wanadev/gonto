"""Bindings for the Win32 File API."""

import sys
import ctypes
import ctypes.wintypes
from enum import IntEnum

# =============================================================================
# Enums
# =============================================================================


class CREATION_DISPOSITION(IntEnum):
    """An action to take on a file or device that exists or does not exist.

    See: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    """

    # fmt: off
    CREATE_NEW        = 1
    CREATE_ALWAYS     = 2
    OPEN_EXISTING     = 3
    OPEN_ALWAYS       = 4
    TRUNCATE_EXISTING = 5
    # fmt: on


# =============================================================================
# Function bindings
# =============================================================================


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.WinDLL("kernel32.dll", use_last_error=True)
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

    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    # HANDLE CreateFileW(
    #   [in]           LPCWSTR               lpFileName,
    #   [in]           DWORD                 dwDesiredAccess,
    #   [in]           DWORD                 dwShareMode,
    #   [in, optional] LPSECURITY_ATTRIBUTES lpSecurityAttributes,
    #   [in]           DWORD                 dwCreationDisposition,
    #   [in]           DWORD                 dwFlagsAndAttributes,
    #   [in, optional] HANDLE                hTemplateFile
    # );
    lib.CreateFileW.argtypes = [
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ns-wtypesbase-security_attributes
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.HANDLE,
    ]
    lib.CreateFileW.restype = ctypes.wintypes.HANDLE

    # https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumepathnamesforvolumenamew
    # BOOL GetVolumePathNamesForVolumeNameW(
    #   [in]  LPCWSTR lpszVolumeName,
    #   [out] LPWCH   lpszVolumePathNames,
    #   [in]  DWORD   cchBufferLength,
    #   [out] PDWORD  lpcchReturnLength
    # );
    lib.GetVolumePathNamesForVolumeNameW.argtypes = [
        ctypes.wintypes.LPCWSTR,
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
        ctypes.POINTER(ctypes.wintypes.DWORD),
    ]
    lib.GetVolumePathNamesForVolumeNameW.restype = ctypes.wintypes.BOOL

    return lib


#: Binding of fileapi functions of ``kernel32.dll``. See source code for a list
#: of bound functions.
lib = _bind_lib()
