"""Bindings for the fmifs win32 API.

This API is not documented by Microsoft, but a header was released in the
past:

* https://github.com/Microsoft/winfile/blob/master/src/fmifs.h
"""

import sys
import ctypes
import ctypes.wintypes
from enum import IntEnum

if sys.platform == "win32":
    from ctypes import WINFUNCTYPE
else:
    # XXX Hack: Allow to lint the code and build the doc on Linux...
    from ctypes import CFUNCTYPE as WINFUNCTYPE


# =============================================================================
# Enums
# =============================================================================


class FMIFS_MEDIA_FLAG(IntEnum):
    """Media flags."""

    # fmt: off
    FLOPPY    = 0x08
    REMOVABLE = 0x0B
    HARDDISK  = 0x0C
    # fmt: on


class FMIFS_PACKET_TYPE(IntEnum):
    """Packet types for :py:const:`FMIFS_CALLBACK`."""

    # fmt: off
    PERCENT_COMPLETED        = 0x00
    FORMAT_REPORT            = 0x01
    INSERT_DISK              = 0x02
    INCOMPATIBLE_FILE_SYSTEM = 0x03
    FORMATTING_DESTINATION   = 0x04
    INCOMPATIBLE_MEDIA       = 0x05
    ACCESS_DENIED            = 0x06
    MEDIA_WRITE_PROTECTED    = 0x07
    CANT_LOCK                = 0x08
    CANT_QUICK_FORMAT        = 0x09
    IO_ERROR                 = 0x0A
    FINISHED                 = 0x0B
    BAD_LABEL                = 0x0C
    CHECK_ON_REBOOT          = 0x0D
    TEXT_MESSAGE             = 0x0E
    HIDDEN_STATUS            = 0x0F
    # fmt: on


# =============================================================================
# Structures
# =============================================================================


class FmifsFinishedInformation(ctypes.Structure):
    """Returned when FMIFS finished to format a volume
    (:py:const:`FMIFS_CALLBACK` ``PacketData`` =
    :py:attr:`FMIFS_PACKET_TYPE.FINISHED`).

    See: https://github.com/microsoft/winfile/blob/master/src/fmifs.h#L78-L80
    """

    _fields_ = [
        ("success", ctypes.wintypes.BOOLEAN),
    ]


# =============================================================================
# Function bindings
# =============================================================================


# typedef BOOLEAN (*FMIFS_CALLBACK)(
#     IN  FMIFS_PACKET_TYPE   PacketType,
#     IN  ULONG               PacketLength,
#     IN  PVOID               PacketData
# );
#
#: Callback function used for formatting progress
#:
#: See: https://github.com/microsoft/winfile/blob/master/src/fmifs.h#L179-L184
FMIFS_CALLBACK = WINFUNCTYPE(
    ctypes.wintypes.BOOLEAN,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.ULONG,
    ctypes.c_void_p,
)


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.windll.LoadLibrary("fmifs.dll")
    else:
        return None

    # https://github.com/Microsoft/winfile/blob/master/src/fmifs.h#L346-L354
    # VOID FormatEx(
    #   IN  PWSTR               DriveName,
    #   IN  FMIFS_MEDIA_TYPE    MediaType,
    #   IN  PWSTR               FileSystemName,
    #   IN  PWSTR               Label,
    #   IN  BOOLEAN             Quick,
    #   IN  ULONG               ClusterSize,
    #   IN  FMIFS_CALLBACK      Callback
    # );
    lib.FormatEx.argtypes = [
        ctypes.wintypes.PWCHAR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.PWCHAR,
        ctypes.wintypes.PWCHAR,
        ctypes.wintypes.BOOLEAN,
        ctypes.wintypes.ULONG,
        FMIFS_CALLBACK,
    ]
    lib.FormatEx.restype = None

    return lib


#: Binding of functions from ``fmifs.dll``. See source code for a
#: list of bound functions.
lib = _bind_lib()
