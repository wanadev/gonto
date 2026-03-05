"""Manipulate disk images (vhd, vhdx, iso) on Windows.

Example mounting of the first volume in the disk image on the first available
drive letter::

    from gonto.diskimage import DiskImage

    disk = DiskImage()
    disk.open("./mydisk.vhd")
    disk.attach()
    # Do stuff
    disk.detach()
    del disk

Example persistent mounting of the first volume of the disk image on a chosen
drive letter::

    from gonto.diskimage import DiskImage
    from gonto.win32.virtdisk import ATTACH_VIRTUAL_DISK_FLAG

    disk = DiskImage()
    disk.open("./mydisk.vhd")
    disk.attach(
        attach_flags=ATTACH_VIRTUAL_DISK_FLAG.NO_DRIVE_LETTER | ATTACH_VIRTUAL_DISK_FLAG.PERMANENT_LIFETIME
    )
    disk.mount_volume("G:\\\\")
"""

import re
import ctypes
import ctypes.wintypes
from pathlib import Path
from collections.abc import Iterator

from .win32 import fileapi
from .win32 import handleapi
from .win32 import ioapiset
from .win32 import virtdisk
from .win32 import winbase
from .win32 import winioctl
from .win32.const import ERROR_SUCCESS
from .win32.const import ERROR_NO_MORE_FILES
from .win32.const import ACCESS_MASK
from .win32.const import FILE_SHARE

_ext_to_device_type = {
    ".iso": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.ISO,
    ".vhd": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.VHD,
    ".vhdx": virtdisk.VIRTUAL_STORAGE_TYPE_DEVICE.VHDX,
}


class BaseDiskImageError(Exception):
    """Base error for Gonto's specific DiskImage errors."""

    pass


class DiskImageNotOpened(BaseDiskImageError):
    """The operation requires an opened disk image but none was opened."""

    pass


class DiskImageAlreadyOpened(BaseDiskImageError):
    """Trying to open a disk image whereas one is already opened in the object."""

    pass


class DiskImageNotAttached(BaseDiskImageError):
    """The operation requires that the disk image was attached."""

    pass


class DiskImageAlreadyAttached(BaseDiskImageError):
    """Trying to attach the disk image whereas it is already attached."""

    pass


class VolumeNotInDiskImage(BaseDiskImageError):
    """The given volume does not belong to the open disk image."""

    pass


class DiskImage:
    """Manipulates a disk image (vhd, vhdx, iso) on Windows."""

    def __init__(self):
        self._handle = None
        self._attached = False

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
            hard disk (default: :py:attr:`.win32.virtdisk.VIRTUAL_DISK_ACCESS_MASK.ALL`).
        :param open_flags: Virtual hard disk open request flags (default:
            :py:attr:`.win32.virtdisk.OPEN_VIRTUAL_DISK_FLAG.NONE`).

        :raise DiskImageAlreadyOpened: If a virtual disk has already been opened.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if self._handle:
            raise DiskImageAlreadyOpened("Virtual disk already opened!")

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
            :py:attr:`.win32.virtdisk.ATTACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageAlreadyAttached: If the disk is already attached. Use
            :py:meth:`DiskImage.detach` to detach the disk first if you want
            to reattach it with different flags.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened!")
        if self._attached:
            raise DiskImageAlreadyAttached("The disk is already attached.")

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

        self._attached = True

    def detach(
        self,
        detach_flags: virtdisk.DETACH_VIRTUAL_DISK_FLAG = virtdisk.DETACH_VIRTUAL_DISK_FLAG.NONE,
    ) -> None:
        """Detaches a virtual hard disk (VHD) or CD or DVD image file (ISO).

        :param detach_flags: Flags for the detach request (default:
            :py:attr:`.win32.virtdisk.DETACH_VIRTUAL_DISK_FLAG.NONE`).

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

        ret = virtdisk.lib.DetachVirtualDisk(
            self._handle,
            detach_flags,
            0x00,
        )

        if ret != ERROR_SUCCESS:
            raise ctypes.WinError(ret)  # type: ignore

        self._attached = False

    def get_physical_path(self) -> str:
        """Retrieves the path to the physical device object that contains a
        virtual hard disk (VHD) or CD or DVD image file (ISO).

        :return: The path of the physical device object.

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """

        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

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

    def get_disk_number(self) -> int:
        """Get the disk number of the current disk image.

        .. important::

           The disk image must be attached!

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise ValueError: If the disk's physical path has an unexpected
            format.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """
        physical_path = self.get_physical_path()
        match = re.match(r".+\\PhysicalDrive(\d+)$", physical_path, re.IGNORECASE)

        if not match:
            raise ValueError("Unexpected physical path: %s" % physical_path)

        return int(match.group(1))

    def is_volume_in_disk_image(self, volume_name: str) -> bool:
        """Checks if the given volume name belongs to the disk image.

        :param volume_name: Path of the volume (``"\\\\?\\Volume{GUID}\\"``).

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """
        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

        # /!\ https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew#:~:text=Do%20not%20use%20a%20trailing%20backslash
        volume_name = volume_name.rstrip("\\")

        _vol_handle = fileapi.lib.CreateFileW(
            volume_name,
            ACCESS_MASK.GENERIC_READ,
            FILE_SHARE.READ | FILE_SHARE.WRITE,
            None,
            fileapi.CREATION_DISPOSITION.OPEN_EXISTING,
            0x00,
            None,
        )

        if _vol_handle == handleapi.INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

        try:
            extents = winioctl.VolumeDiskExtents()
            bytes_returned = ctypes.wintypes.DWORD()

            success = ioapiset.lib.DeviceIoControl(
                _vol_handle,
                winioctl.IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS,
                None,
                0,
                ctypes.byref(extents),
                ctypes.sizeof(extents),
                ctypes.byref(bytes_returned),
                None,
            )

            if not success:
                raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

            disk_number = self.get_disk_number()

            for i in range(extents.number_of_disk_extents):
                if extents.extents[i].disk_number == disk_number:
                    return True
        finally:
            handleapi.lib.CloseHandle(_vol_handle)

        return False

    def list_volumes(self) -> Iterator[str]:
        """List volumes available in the disk image.

        :returns: The available volumes.

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """
        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

        _volume_name_p = ctypes.create_unicode_buffer(1024)
        buffer_length = 1024  # WARN: Length in TCHARs (a.k.a WCHAR in our case)

        _find_handle = fileapi.lib.FindFirstVolumeW(_volume_name_p, buffer_length)

        if _find_handle == handleapi.INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

        try:
            try:
                if self.is_volume_in_disk_image(_volume_name_p.value):
                    yield _volume_name_p.value
            except OSError:
                pass  # Can't access the volume -> skip it.

            while fileapi.lib.FindNextVolumeW(
                _find_handle, _volume_name_p, buffer_length
            ):
                try:
                    if self.is_volume_in_disk_image(_volume_name_p.value):
                        yield _volume_name_p.value
                except OSError:
                    pass  # Can't access the volume -> skip it.

            if ctypes.get_last_error() != ERROR_NO_MORE_FILES:  # type: ignore
                raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

        finally:
            fileapi.lib.FindVolumeClose(_find_handle)
            # Note: silently ignore errors that may occur when closing the handle

    def mount_volume(self, mount_point: str, volume_name: str | None = None) -> None:
        """Mount a volume in the image disk with the given drive letter.

        :param mount_point: The drive letter or the directory where the volume
            will be mounted (e.g. ``"G:\\\\"``, ``"C:\\\\MyEmptyFolder\\\\"``).

            .. IMPORTANT::

               The mount path must ends with a trailing backslash (``\\``).

        :param volume_name: The id of the volume to mount
            (``\\\\?\\Volume{GUID}\\``) or ``None`` to mount the first volume of the
            disk.

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise VolumeNotInDiskImage: If the given volume name does not belong
            to the current disk image.
        :raise WindowsError|OSError: If a Win32 error occurs.
        """
        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

        if not volume_name:
            volume_name = next(self.list_volumes())
        elif not self.is_volume_in_disk_image(volume_name):
            raise VolumeNotInDiskImage(
                "Volume not in the opened disk image: %s" % volume_name
            )

        success = winbase.lib.SetVolumeMountPointW(mount_point, volume_name)

        if not success:
            raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

    def get_volume_mount_point(self, volume_name: str | None = None) -> str | None:
        """Get the mount point of the given volume.

        :param volume_name: The name of a volume in the image disk or ``None``
            for the first volume of the image disk.

        :raise DiskImageNotOpened: If no virtual disk image was opened using
            the :py:meth:`DiskImage.open` method.
        :raise DiskImageNotAttached: If the virtual disk image was not attached
            using the :py:meth:`DiskImage.attach` method.
        :raise VolumeNotInDiskImage: If the given volume name does not belong
            to the current disk image.
        :raise WindowsError|OSError: If a Win32 error occurs.

        :return: The mount point of the volume or ``None`` if it is not mounted.

            .. IMPORTANT::

               For sake of simplicity, we only handle ONE mount point per volume.
               If the volume has multiple mount points, only the first one will be
               returned.
        """
        if not self._handle:
            raise DiskImageNotOpened("No virtual disk opened")
        if not self._attached:
            raise DiskImageNotAttached("The disk is not attached")

        if not volume_name:
            volume_name = next(self.list_volumes())
        else:
            if not self.is_volume_in_disk_image(volume_name):
                raise VolumeNotInDiskImage(
                    "Volume not in the opened disk image: %s" % volume_name
                )

        _volume_path_names_buffer_p = ctypes.create_unicode_buffer(1024)
        buffer_length = 1024  # WARN: Length in WCHARs
        _return_length = ctypes.wintypes.DWORD()

        success = fileapi.lib.GetVolumePathNamesForVolumeNameW(
            volume_name,
            _volume_path_names_buffer_p,
            buffer_length,
            ctypes.byref(_return_length),
        )

        if not success:
            raise ctypes.WinError(ctypes.get_last_error())  # type: ignore

        if not _volume_path_names_buffer_p.value:
            return None  # Not mounted

        return _volume_path_names_buffer_p.value

    def __del__(self) -> None:
        if not self._handle:
            return
        handleapi.lib.CloseHandle(self._handle)
        self._handle = None
        self._attached = False
