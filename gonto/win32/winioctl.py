"""Bindings for the Win32 IoApiCtl API."""

import ctypes
import ctypes.wintypes
from enum import IntEnum

# =============================================================================
# Helpers
# =============================================================================


# #define CTL_CODE( DeviceType, Function, Method, Access ) (                 \
#     ((DeviceType) << 16) | ((Access) << 14) | ((Function) << 2) | (Method) \
# )
def _ctl_code(device_type: int, function: int, method: int, access: int) -> int:
    """Defining IOCTL and FSCTL function control codes.

    See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L264C25-L264C73
    """
    return device_type << 16 | access << 14 | function << 2 | method


# =============================================================================
# Enums
# =============================================================================


class METHOD(IntEnum):
    """Define the method codes for how buffers are passed for I/O and FS controls.

    See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L287
    """

    # fmt: off
    BUFFERED   = 0
    IN_DIRECT  = 1
    OUT_DIRECT = 2
    NEITHER    = 3
    # fmt: on


class FILE_ACCESS(IntEnum):
    """Define the access check value for any access.

    See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L301
    """

    # fmt: off
    ANY     = 0x0000
    SPECIAL = 0x0000
    READ    = 0x0001
    WRITE   = 0x0002
    # fmt: on


# =============================================================================
# Structures
# =============================================================================


class DiskExtent(ctypes.Structure):
    """Represents a disk extent.

    See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-disk_extent
    """

    _fields_ = [
        ("disk_number", ctypes.wintypes.DWORD),
        ("starting_offset", ctypes.wintypes.LARGE_INTEGER),
        ("extent_length", ctypes.wintypes.LARGE_INTEGER),
    ]


class VolumeDiskExtents(ctypes.Structure):
    """Represents a physical location on a disk. It is the output buffer for
    the :py:attr:`IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS` control code.

    See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-volume_disk_extents
    """

    _fields_ = [
        ("number_of_disk_extents", ctypes.wintypes.DWORD),
        ("extents", DiskExtent * 1),
    ]


# =============================================================================
# Constants
# =============================================================================

#: See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L17713
IOCTL_VOLUME_BASE = 0x00000056

#: IOCTL to obtain the physical location of the specified volume on one or more
#: disks.
IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = _ctl_code(
    IOCTL_VOLUME_BASE,
    0,
    METHOD.BUFFERED,
    FILE_ACCESS.ANY,
)
