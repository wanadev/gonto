import ctypes
import ctypes.wintypes
import uuid
from enum import IntEnum, Enum, IntFlag
from pathlib import Path

from .const import ERROR_SUCCESS


class VIRTUAL_STORAGE_TYPE_DEVICE(IntEnum):
    """Device type identifier.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-virtual_storage_type#members
    """

    # fmt: off
    UNKNOWN = 0
    ISO     = 1
    VHD     = 2
    VHDX    = 3
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
    # NON_PNP,
    # RESTRICTED_RANGE,
    # SINGLE_PARTITION,
    # REGISTER_VOLUME,
    # AT_BOOT
    # fmt: on


class DETACH_VIRTUAL_DISK_FLAG(IntFlag):
    """Contains virtual disk detach request flags.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ne-virtdisk-detach_virtual_disk_flag
    """

    NONE = 0x00000000


class VirtualStorageType(ctypes.Structure):
    """Contains the type and provider (vendor) of the virtual storage device.

    See: https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-virtual_storage_type
    """

    _fields_ = [
        ("device_id", ctypes.wintypes.ULONG),
        ("guid", ctypes.c_char * 16),
    ]


class VirtDisk:
    """High-Level binding of the VirtDisk Win32 API."""

    def __init__(self):
        self._win32_virtdisk = ctypes.windll.LoadLibrary("virtdisk.dll")
        self._win32_kernel32 = ctypes.windll.LoadLibrary("kernel32.dll")
        self._handle = None

    def open(
        self,
        path: Path | str,
        device_type: VIRTUAL_STORAGE_TYPE_DEVICE | None = None,
        access_mask: VIRTUAL_DISK_ACCESS_MASK = VIRTUAL_DISK_ACCESS_MASK.ALL,
        open_flags: OPEN_VIRTUAL_DISK_FLAG = OPEN_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Opens a virtual hard disk (VHD) or CD or DVD image file (ISO) for
        use.

        :param path: Path to the disk image.
        :param device_type: The type of the disk image (default: ``None``
            (guessed from file extension)).
        :param access_mask: Bitmask for specifying access rights to a virtual
            hard disk (default: :py:attr:`VIRTUAL_DISK_ACCESS_MASK.ALL`).
        :param open_flags: Virtual hard disk open request flags (default:
            :py:attr:`OPEN_VIRTUAL_DISK_FLAG.NONE`).

        :raise WindowsError|OSError: If a Win32 error occurs.
        :raise IOError: If a virtual disk has already been opened.
        """

        if self._handle:
            raise IOError("Virtual disk already opened!")

        ext_to_device_type = {
            ".iso": VIRTUAL_STORAGE_TYPE_DEVICE.ISO,
            ".vhd": VIRTUAL_STORAGE_TYPE_DEVICE.VHD,
            ".vhdx": VIRTUAL_STORAGE_TYPE_DEVICE.VHDX,
        }

        path = Path(path)

        # Guess device_type from file ext
        if device_type is None:
            ext = path.suffix.lower()
            if ext in ext_to_device_type:
                device_type = ext_to_device_type[ext]
            else:
                device_type = VIRTUAL_STORAGE_TYPE_DEVICE.UNKNOWN

        _virtual_storage_type = VirtualStorageType(
            device_id=device_type.value,
            guid=VIRTUAL_STORAGE_TYPE_VENDOR.MICROSOFT.value,
        )

        _path_p = ctypes.c_wchar_p(str(path))
        _handle = ctypes.wintypes.HANDLE()

        # DWORD OpenVirtualDisk(
        #   [in]           PVIRTUAL_STORAGE_TYPE         VirtualStorageType,
        #   [in]           PCWSTR                        Path,
        #   [in]           VIRTUAL_DISK_ACCESS_MASK      VirtualDiskAccessMask,
        #   [in]           OPEN_VIRTUAL_DISK_FLAG        Flags,
        #   [in, optional] POPEN_VIRTUAL_DISK_PARAMETERS Parameters,
        #   [out]          PHANDLE                       Handle
        # );
        # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-openvirtualdisk
        self._win32_virtdisk.OpenVirtualDisk.argtypes = [
            ctypes.POINTER(VirtualStorageType),
            ctypes.wintypes.LPCWSTR,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.DWORD,
            ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
            ctypes.wintypes.PHANDLE,
        ]
        self._win32_virtdisk.OpenVirtualDisk.restype = ctypes.wintypes.DWORD
        ret = self._win32_virtdisk.OpenVirtualDisk(
            _virtual_storage_type,
            _path_p,
            access_mask,
            open_flags,
            None,  # XXX https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-open_virtual_disk_parameters
            ctypes.byref(_handle),
        )

        if ret != ERROR_SUCCESS or _handle.value is None:
            raise ctypes.WinError(ret)  # type: ignore

        self._handle = _handle

    def attach(
        self,
        attach_flags: ATTACH_VIRTUAL_DISK_FLAG = ATTACH_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Attaches a virtual hard disk (VHD) or CD or DVD image file (ISO).

        :param attach_flags: Flags for the attach request (default:
            :py:attr:`ATTACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise IOError: If the virtual disk was not opened using the
            :py:meth:`VirtDisk.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        # DWORD AttachVirtualDisk(
        #   [in]           HANDLE                          VirtualDiskHandle,
        #   [in, optional] PSECURITY_DESCRIPTOR            SecurityDescriptor,
        #   [in]           ATTACH_VIRTUAL_DISK_FLAG        Flags,
        #   [in]           ULONG                           ProviderSpecificFlags,
        #   [in, optional] PATTACH_VIRTUAL_DISK_PARAMETERS Parameters,
        #   [in, optional] LPOVERLAPPED                    Overlapped
        # );
        # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-attachvirtualdisk
        self._win32_virtdisk.AttachVirtualDisk.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
            ctypes.wintypes.DWORD,
            ctypes.wintypes.ULONG,
            ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
            ctypes.c_void_p,  # XXX Improve this definition if we bind the struct
        ]
        self._win32_virtdisk.AttachVirtualDisk.restype = ctypes.wintypes.DWORD
        ret = self._win32_virtdisk.AttachVirtualDisk(
            self._handle,
            None,  # XXX https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_descriptor
            attach_flags,
            0x00,
            None,  # XXX https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/ns-virtdisk-attach_virtual_disk_parameters
            None,  # XXX https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped
        )

        if ret != ERROR_SUCCESS:
            raise ctypes.WinError(ret)  # type: ignore

    def detach(
        self,
        detach_flags: DETACH_VIRTUAL_DISK_FLAG = DETACH_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Detaches a virtual hard disk (VHD) or CD or DVD image file (ISO).

        :param detach_flags: Flags for the detach request (default:
            :py:attr:`DETACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise IOError: If the virtual disk was not opened using the
            :py:meth:`VirtDisk.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        # DWORD DetachVirtualDisk(
        #   [in] HANDLE                   VirtualDiskHandle,
        #   [in] DETACH_VIRTUAL_DISK_FLAG Flags,
        #   [in] ULONG                    ProviderSpecificFlags
        # );
        # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-detachvirtualdisk
        self._win32_virtdisk.DetachVirtualDisk.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.DWORD,
            ctypes.wintypes.ULONG,
        ]
        self._win32_virtdisk.DetachVirtualDisk.restype = ctypes.wintypes.DWORD
        ret = self._win32_virtdisk.DetachVirtualDisk(
            self._handle,
            detach_flags,
            0x00,
        )

        if ret != ERROR_SUCCESS:
            raise ctypes.WinError(ret)  # type: ignore

    def get_physical_path(self) -> str:
        """Retrieves the path to the physical device object that contains a
        virtual hard disk (VHD) or CD or DVD image file (ISO).

        :rtype: str
        :return: The path of the physical device object.

        :raise IOError: If the virtual disk was not opened using the
            :py:meth:`VirtDisk.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        _path_p = ctypes.create_unicode_buffer(1024)
        _size = ctypes.wintypes.ULONG(ctypes.sizeof(_path_p))

        # DWORD GetVirtualDiskPhysicalPath(
        #   [in]            HANDLE VirtualDiskHandle,
        #   [in, out]       PULONG DiskPathSizeInBytes,
        #   [out, optional] PWSTR  DiskPath
        # )
        # https://learn.microsoft.com/en-us/windows/win32/api/virtdisk/nf-virtdisk-getvirtualdiskphysicalpath
        self._win32_virtdisk.GetVirtualDiskPhysicalPath.argtypes = [
            ctypes.wintypes.HANDLE,
            ctypes.wintypes.PULONG,
            ctypes.wintypes.LPWSTR,
        ]
        self._win32_virtdisk.GetVirtualDiskPhysicalPath.restype = ctypes.wintypes.DWORD
        ret = self._win32_virtdisk.GetVirtualDiskPhysicalPath(
            self._handle,
            ctypes.byref(_size),
            _path_p,
        )

        if ret != ERROR_SUCCESS:
            raise ctypes.WinError(ret)  # type: ignore

        return _path_p.value

    def __del__(self) -> None:
        if not self._handle:
            return
        if not self._win32_kernel32:
            return
        self._win32_kernel32.CloseHandle(self._handle)
        self._handle = None
