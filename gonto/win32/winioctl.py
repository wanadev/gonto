"""Bindings for the Win32 IoApiCtl API."""

import ctypes
import ctypes.wintypes
import uuid
from enum import Enum, IntEnum

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


class PARTITION_STYLE(IntEnum):
    """Represents the format of a partition.

    See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ne-winioctl-partition_style
    """

    MBR = 0
    GPT = 1
    RAW = 2


class PARTITION_TYPE_GUID(Enum):
    """GUIDs that identifies partition types.

    See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-partition_information_gpt
    """

    BASIC_DATA = uuid.UUID("ebd0a0a2-b9e5-4433-87c0-68b6b72699c7").bytes_le
    ENTRY_UNUSED = uuid.UUID("00000000-0000-0000-0000-000000000000").bytes_le
    SYSTEM = uuid.UUID("c12a7328-f81f-11d2-ba4b-00a0c93ec93b").bytes_le
    MSFT_RESERVED = uuid.UUID("e3c9e316-0b5c-4db8-817d-f92df00215ae").bytes_le
    LDM_METADATA = uuid.UUID("5808c8aa-7e8f-42e0-85d2-e1e90434cfb3").bytes_le
    LDM_DATA = uuid.UUID("af9b60a0-1431-4f62-bc68-3311714a69ad").bytes_le
    MSFT_RECOVERY = uuid.UUID("de94bba4-06d1-4d40-a16a-bfd50179d6ac").bytes_le


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


class CreateDiskGPT(ctypes.Structure):
    """Contains information that the IOCTL_DISK_CREATE_DISK control code uses
    to initialize GPT partition table (flattened GPT version).

    .. WARNING::

       The ``partition_style`` field MUST be set to :attr:`PARTITION_STYLE.GPT`.

    See:

    * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-create_disk
    * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-create_disk_gpt
    """

    _fields_ = [
        ("partition_style", ctypes.wintypes.DWORD),  # MUST be PARTITION_STYLE.GPT
        ("guid", ctypes.c_char * 16),
        ("max_partition_count", ctypes.wintypes.DWORD),
        # ↑↑ min = 128 for compliance with EFI spec
    ]


class PartitionInformationExGPT(ctypes.Structure):
    """Contains GPT partition information.

    See:

    * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-partition_information_ex
    * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-partition_information_gpt
    """

    _fields_ = [
        ("partition_style", ctypes.wintypes.DWORD),  # One of PARTITION_STYLE enum
        ("partition_ordinal", ctypes.wintypes.WORD),
        ("starting_offset", ctypes.wintypes.LARGE_INTEGER),
        ("partition_length", ctypes.wintypes.LARGE_INTEGER),
        ("partition_number", ctypes.wintypes.DWORD),
        ("rewrite_partition", ctypes.wintypes.BOOLEAN),
        ("is_service_partition", ctypes.wintypes.BOOLEAN),
        ("_padding", ctypes.c_char * 2),  # Padding (because struct was flattened)
        # ↓↓ GPT
        ("partition_type", ctypes.c_char * 16),
        ("partition_id", ctypes.c_char * 16),
        ("attributes", ctypes.c_uint64),  # DWORD64
        ("name", ctypes.wintypes.WCHAR * 36),
    ]


def drive_layout_information_ex_gpt_factory(
    partition_count: int = 1, **params
) -> ctypes.Structure:
    """Generate a :py:class:`DriveLayoutInformationExGPT` structure which can store the
    information for ``partition_count`` partitions.

    :param partition_count: The number of partitions (default: 1).
    :param params: Any member of the :py:class:`DriveLayoutInformationExGPT`
        struct to initialize values.

    .. py:class:: DriveLayoutInformationExGPT

       Contains extended information about a drive's partitions (flattened GPT variant).

       See:

       * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-drive_layout_information_ex
       * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-drive_layout_information_gpt

       .. py:attribute:: partition_style
       .. py:attribute:: partition_count
       .. py:attribute:: disk_id
       .. py:attribute:: starting_usable_offset
       .. py:attribute:: usable_length
       .. py:attribute:: max_partition_count
       .. py:attribute:: partition_entry
    """

    class DriveLayoutInformationExGPT(ctypes.Structure):
        """Contains extended information about a drive's partitions (GPT variant).

        See:

        * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-drive_layout_information_ex
        * https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ns-winioctl-drive_layout_information_gpt
        """

        _fields_ = [
            ("partition_style", ctypes.wintypes.DWORD),
            ("partition_count", ctypes.wintypes.DWORD),
            # ↓↓ GPT
            ("disk_id", ctypes.c_char * 16),
            ("starting_usable_offset", ctypes.wintypes.LARGE_INTEGER),
            ("usable_length", ctypes.wintypes.LARGE_INTEGER),
            ("max_partition_count", ctypes.wintypes.DWORD),
            # ↑↑ GPT
            ("partition_entry", PartitionInformationExGPT * partition_count),
        ]

    return DriveLayoutInformationExGPT(partition_count=partition_count, **params)


# =============================================================================
# Constants
# =============================================================================

#: See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L17713
IOCTL_VOLUME_BASE = 0x00000056

#: IOCTL to obtain the physical location of the specified volume on one or more
#: disks.
#:
#: See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_volume_get_volume_disk_extents
IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = _ctl_code(
    IOCTL_VOLUME_BASE,
    0,
    METHOD.BUFFERED,
    FILE_ACCESS.ANY,
)

#: See: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winioctl.h#L9013
IOCTL_DISK_BASE = 0x00000007

#: Initializes the specified disk and disk partition table using the
#: information in the CREATE_DISK structure.
#:
#: See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_disk_create_disk
IOCTL_DISK_CREATE_DISK = _ctl_code(
    IOCTL_DISK_BASE,
    0x0016,
    METHOD.BUFFERED,
    FILE_ACCESS.READ | FILE_ACCESS.WRITE,
)

#: Invalidates the cached partition table and re-enumerates the device.
#:
#: See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_disk_update_properties
IOCTL_DISK_UPDATE_PROPERTIES = _ctl_code(
    IOCTL_DISK_BASE,
    0x0050,
    METHOD.BUFFERED,
    FILE_ACCESS.ANY,
)

#: Retrieves extended information for each entry in the partition tables for a
#: disk.
#:
#: See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_disk_get_drive_layout_ex
IOCTL_DISK_GET_DRIVE_LAYOUT_EX = _ctl_code(
    IOCTL_DISK_BASE,
    0x0014,
    METHOD.BUFFERED,
    FILE_ACCESS.ANY,
)

#: Partitions a disk according to the specified drive layout and partition
#: information data.
#:
#: See: https://learn.microsoft.com/en-us/windows/win32/api/winioctl/ni-winioctl-ioctl_disk_set_drive_layout_ex
IOCTL_DISK_SET_DRIVE_LAYOUT_EX = _ctl_code(
    IOCTL_DISK_BASE,
    0x0015,
    METHOD.BUFFERED,
    FILE_ACCESS.READ | FILE_ACCESS.WRITE,
)
