import ctypes
import ctypes.wintypes
from pathlib import Path

from .win32 import virtdisk
from .win32 import handleapi
from .win32.const import ERROR_SUCCESS

_ext_to_device_type = {
    ".iso": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.ISO,
    ".vhd": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.VHD,
    ".vhdx": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.VHDX,
}


class DiskImage:
    """Manipulates a disk image (vhd, vhdx, iso) on Windows."""

    def __init__(self):
        self._handle = None

    def open(
        self,
        path: Path | str,
        device_type: virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE | None = None,
        access_mask: virtdisk.VIRTUAL_DISK_ACCESS_MASK = virtdisk.VIRTUAL_DISK_ACCESS_MASK.ALL,
        open_flags: virtdisk.OPEN_VIRTUAL_DISK_FLAG = virtdisk.OPEN_VIRTUAL_DISK_FLAG.NONE,
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

        path = Path(path)

        # Guess device_type from file ext
        if device_type is None:
            ext = path.suffix.lower()
            if ext in _ext_to_device_type:
                device_type = _ext_to_device_type[ext]
            else:
                device_type = virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.UNKNOWN

        _virtual_storage_type = virtdisk.VirtualStorageType(
            device_id=device_type.value,
            guid=virtdisk.VIRTUAL_STORAGE_TYPE_VENDOR.MICROSOFT.value,
        )

        _path_p = ctypes.c_wchar_p(str(path))
        _handle = ctypes.wintypes.HANDLE()

        ret = virtdisk.lib.OpenVirtualDisk(
            _virtual_storage_type,
            _path_p,
            access_mask,
            open_flags,
            None,
            ctypes.byref(_handle),
        )

        if ret != ERROR_SUCCESS or _handle.value is None:
            raise ctypes.WinError(ret)  # type: ignore

        self._handle = _handle

    def attach(
        self,
        attach_flags: virtdisk.ATTACH_VIRTUAL_DISK_FLAG = virtdisk.ATTACH_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Attaches a virtual hard disk (VHD) or CD or DVD image file (ISO).

        :param attach_flags: Flags for the attach request (default:
            :py:attr:`ATTACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise IOError: If the virtual disk was not opened using the
            :py:meth:`DiskImage.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        ret = virtdisk.lib.AttachVirtualDisk(
            self._handle,
            None,
            attach_flags,
            0x00,
            None,
            None,
        )

        if ret != ERROR_SUCCESS:
            raise ctypes.WinError(ret)  # type: ignore

    def detach(
        self,
        detach_flags: virtdisk.DETACH_VIRTUAL_DISK_FLAG = virtdisk.DETACH_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Detaches a virtual hard disk (VHD) or CD or DVD image file (ISO).

        :param detach_flags: Flags for the detach request (default:
            :py:attr:`DETACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise IOError: If the virtual disk was not opened using the
            :py:meth:`DiskImage.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        ret = virtdisk.lib.DetachVirtualDisk(
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
            :py:meth:`DiskImage.open` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise IOError("No virtual disk opened!")

        _path_p = ctypes.create_unicode_buffer(1024)
        _size = ctypes.wintypes.ULONG(ctypes.sizeof(_path_p))

        ret = virtdisk.lib.GetVirtualDiskPhysicalPath(
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
        handleapi.lib.CloseHandle(self._handle)
        self._handle = None
