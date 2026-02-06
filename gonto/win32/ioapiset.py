"""Bindings for the Win32 IoApiSet API."""

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

    # https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-deviceiocontrol
    # BOOL DeviceIoControl(
    #   [in]                HANDLE       hDevice,
    #   [in]                DWORD        dwIoControlCode,
    #   [in, optional]      LPVOID       lpInBuffer,
    #   [in]                DWORD        nInBufferSize,
    #   [out, optional]     LPVOID       lpOutBuffer,
    #   [in]                DWORD        nOutBufferSize,
    #   [out, optional]     LPDWORD      lpBytesReturned,
    #   [in, out, optional] LPOVERLAPPED lpOverlapped
    # );
    lib.DeviceIoControl.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.LPVOID,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.LPVOID,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.LPDWORD,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
    ]
    lib.DeviceIoControl.restype = ctypes.wintypes.BOOL

    return lib


#: Binding of ioapiset functions of ``kernel32.dll``. See source code for a list
#: of bound functions.
lib = _bind_lib()
