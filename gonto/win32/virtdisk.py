"""Bindings for the Win32 VirtDisk API."""

import sys
import ctypes
import ctypes.wintypes
import uuid
from enum import IntEnum, Enum, IntFlag

# =============================================================================
# Enums
# =============================================================================


class VIRTUAL_STORAGE_TYPE(IntEnum):
    """Device type identifier.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-virtual_storage_type#members
    """

    # fmt: off
    DEVICE_UNKNOWN = 0
    DEVICE_ISO     = 1
    DEVICE_VHD     = 2
    DEVICE_VHDX    = 3
    # fmt: on


class VIRTUAL_STORAGE_TYPE_VENDOR(Enum):
    """Vendor-unique identifier.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-virtual_storage_type#virtual_storage_type_vendor_microsoft-ec984aec-a0f9-47e9-901f-71415a66345b
    """

    MICROSOFT = uuid.UUID("EC984AEC-A0F9-47e9-901F-71415A66345B").bytes_le
    UNKNOWN = None


class VIRTUAL_DISK_ACCESS_MASK(IntFlag):
    """Contains the bitmask for specifying access rights to a virtual hard disk
    (VHD) or CD or DVD image file (ISO).

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-virtual_disk_access_mask-r1
    """

    # fmt: off
    NONE      = 0x00000000
    ATTACH_RO = 0x00010000
    ATTACH_RW = 0x00020000
    DETACH    = 0x00040000
    GET_INFO  = 0x00080000
    CREATE    = 0x00100000
    METAOPS   = 0x00200000
    READ      = 0x000d0000
    ALL       = 0x003f0000
    WRITABLE  = 0x00320000
    # fmt: on


class OPEN_VIRTUAL_DISK_FLAG(IntFlag):
    """Contains virtual hard disk (VHD) or CD or DVD image file (ISO) open
    request flags.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-open_virtual_disk_flag
    """

    # fmt: off
    NONE                           = 0x00000000
    NO_PARENTS                     = 0x00000001
    BLANK_FILE                     = 0x00000002
    BOOT_DRIVE                     = 0x00000004
    CACHED_IO                      = 0x00000008
    CUSTOM_DIFF_CHAIN              = 0x00000010
    PARENT_CACHED_IO               = 0x00000020
    VHDSET_FILE_ONLY               = 0x00000040
    IGNORE_RELATIVE_PARENT_LOCATOR = 0x00000080
    NO_WRITE_HARDENING             = 0x00000100
    # SUPPORT_COMPRESSED_VOLUMES
    # SUPPORT_SPARSE_FILES_ANY_FS
    # SUPPORT_ENCRYPTED_FILES
    # fmt: on


class ATTACH_VIRTUAL_DISK_FLAG(IntFlag):
    """Contains virtual disk attach request flags.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-attach_virtual_disk_flag
    """

    # fmt: off
    NONE                             = 0x00000000
    READ_ONLY                        = 0x00000001
    NO_DRIVE_LETTER                  = 0x00000002
    PERMANENT_LIFETIME               = 0x00000004
    NO_LOCAL_HOST                    = 0x00000008
    NO_SECURITY_DESCRIPTOR           = 0x00000010
    BYPASS_DEFAULT_ENCRYPTION_POLICY = 0x00000020
    # NON_PNP
    # RESTRICTED_RANGE
    # SINGLE_PARTITION
    # REGISTER_VOLUME
    # AT_BOOT
    # fmt: on


class DETACH_VIRTUAL_DISK_FLAG(IntFlag):
    """Contains virtual disk detach request flags.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-detach_virtual_disk_flag
    """

    NONE = 0x00000000


class CREATE_VIRTUAL_DISK_FLAG(IntFlag):
    """Contains virtual hard disk (VHD) creation flags.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-create_virtual_disk_flag
    """

    # fmt: off
    NONE                                   = 0x00000000
    FULL_PHYSICAL_ALLOCATION               = 0x00000001
    PREVENT_WRITES_TO_SOURCE_DISK          = 0x00000002
    DO_NOT_COPY_METADATA_FROM_PARENT       = 0x00000004
    CREATE_BACKING_STORAGE                 = 0x00000008
    USE_CHANGE_TRACKING_SOURCE_LIMIT       = 0x00000010
    PRESERVE_PARENT_CHANGE_TRACKING_STATE  = 0x00000020
    VHD_SET_USE_ORIGINAL_BACKING_STORAGE   = 0x00000040
    SPARSE_FILE                            = 0x00000080
    PMEM_COMPATIBLE                        = 0x00000100
    # SUPPORT_COMPRESSED_VOLUMES
    # SUPPORT_SPARSE_FILES_ANY_FS
    # fmt: on


class CREATE_VIRTUAL_DISK_VERSION(IntEnum):
    """Contains the version of the virtual disk CREATE_VIRTUAL_DISK_PARAMETERS
    structure to use in calls to virtual disk functions.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-create_virtual_disk_version
    """

    UNSPECIFIED = 0  # Not supported
    VERSION_1 = 1
    VERSION_2 = 2
    VERSION_3 = 3  # Not documented
    VERSION_4 = 4  # Not documented


# =============================================================================
# Structures
# =============================================================================


class VirtualStorageType(ctypes.Structure):
    """Contains the type and provider (vendor) of the virtual storage device.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-virtual_storage_type
    """

    _fields_ = [
        ("device_id", ctypes.wintypes.ULONG),
        ("guid", ctypes.c_char * 16),
    ]


class CreateVirtualDiskParametersVersion1(ctypes.Structure):
    """Contains virtual hard disk (VHD) creation parameters, providing control
    over, and information about, the newly created virtual disk.

    .. WARNING::

       The ``version`` field MUST be set to :attr:`~CREATE_VIRTUAL_DISK_VERSION.VERSION_1`.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-create_virtual_disk_parameters
    """

    _fields_ = [
        ("version", ctypes.wintypes.DWORD),  # MUST be set to VERSION_1
        ("guid", ctypes.c_char * 16),
        ("maximum_size", ctypes.c_uint64),
        ("block_size_in_bytes", ctypes.wintypes.ULONG),
        ("sector_size_in_bytes", ctypes.wintypes.ULONG),
        ("parent_path", ctypes.wintypes.LPCWSTR),
        ("source_path", ctypes.wintypes.LPCWSTR),
    ]


# =============================================================================
# Function bindings
# =============================================================================


def _bind_lib():
    if sys.platform == "win32":
        lib = ctypes.WinDLL("virtdisk.dll", use_last_error=True)
    else:
        return None

    # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-openvirtualdisk
    # DWORD OpenVirtualDisk(
    #   [in]           PVIRTUAL_STORAGE_TYPE         VirtualStorageType,
    #   [in]           PCWSTR                        Path,
    #   [in]           VIRTUAL_DISK_ACCESS_MASK      VirtualDiskAccessMask,
    #   [in]           OPEN_VIRTUAL_DISK_FLAG        Flags,
    #   [in, optional] POPEN_VIRTUAL_DISK_PARAMETERS Parameters,
    #   [out]          PHANDLE                       Handle
    # );
    lib.OpenVirtualDisk.argtypes = [
        ctypes.POINTER(VirtualStorageType),
        ctypes.wintypes.LPCWSTR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-open_virtual_disk_parameters
        ctypes.wintypes.PHANDLE,
    ]
    lib.OpenVirtualDisk.restype = ctypes.wintypes.DWORD

    # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-attachvirtualdisk
    # DWORD AttachVirtualDisk(
    #   [in]           HANDLE                          VirtualDiskHandle,
    #   [in, optional] PSECURITY_DESCRIPTOR            SecurityDescriptor,
    #   [in]           ATTACH_VIRTUAL_DISK_FLAG        Flags,
    #   [in]           ULONG                           ProviderSpecificFlags,
    #   [in, optional] PATTACH_VIRTUAL_DISK_PARAMETERS Parameters,
    #   [in, optional] LPOVERLAPPED                    Overlapped
    # );
    lib.AttachVirtualDisk.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_descriptor
        ctypes.wintypes.DWORD,
        ctypes.wintypes.ULONG,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-attach_virtual_disk_parameters
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
    ]
    lib.AttachVirtualDisk.restype = ctypes.wintypes.DWORD

    # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-detachvirtualdisk
    # DWORD DetachVirtualDisk(
    #   [in] HANDLE                   VirtualDiskHandle,
    #   [in] DETACH_VIRTUAL_DISK_FLAG Flags,
    #   [in] ULONG                    ProviderSpecificFlags
    # );
    lib.DetachVirtualDisk.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.ULONG,
    ]
    lib.DetachVirtualDisk.restype = ctypes.wintypes.DWORD

    # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-getvirtualdiskphysicalpath
    # DWORD GetVirtualDiskPhysicalPath(
    #   [in]            HANDLE VirtualDiskHandle,
    #   [in, out]       PULONG DiskPathSizeInBytes,
    #   [out, optional] PWSTR  DiskPath
    # )
    lib.GetVirtualDiskPhysicalPath.argtypes = [
        ctypes.wintypes.HANDLE,
        ctypes.wintypes.PULONG,
        ctypes.wintypes.LPWSTR,
    ]
    lib.GetVirtualDiskPhysicalPath.restype = ctypes.wintypes.DWORD

    # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-createvirtualdisk
    # DWORD CreateVirtualDisk(
    #   [in]           PVIRTUAL_STORAGE_TYPE           VirtualStorageType,
    #   [in]           PCWSTR                          Path,
    #   [in]           VIRTUAL_DISK_ACCESS_MASK        VirtualDiskAccessMask,
    #   [in, optional] PSECURITY_DESCRIPTOR            SecurityDescriptor,
    #   [in]           CREATE_VIRTUAL_DISK_FLAG        Flags,
    #   [in]           ULONG                           ProviderSpecificFlags,
    #   [in]           PCREATE_VIRTUAL_DISK_PARAMETERS Parameters,
    #   [in, optional] LPOVERLAPPED                    Overlapped,
    #   [out]          PHANDLE                         Handle
    # );
    lib.CreateVirtualDisk.argtypes = [
        ctypes.POINTER(VirtualStorageType),
        ctypes.wintypes.LPCWSTR,
        ctypes.wintypes.DWORD,
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_descriptor
        ctypes.wintypes.DWORD,
        ctypes.wintypes.ULONG,
        ctypes.POINTER(CreateVirtualDiskParametersVersion1),  # XXX v2 not bound yet
        ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        #                 # XXX https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
        ctypes.wintypes.PHANDLE,
    ]
    lib.CreateVirtualDisk.restype = ctypes.wintypes.DWORD

    return lib


#: Binding of ``virtdisk.dll``. See source code for a list of bound functions.
lib = _bind_lib()
