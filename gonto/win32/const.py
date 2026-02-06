from enum import IntEnum, IntFlag

#: Win32: The operation completed successfully.
ERROR_SUCCESS = 0x00000000

#: Win32: There are no more files.
ERROR_NO_MORE_FILES = 0x00000012


class ACCESS_MASK(IntEnum):
    """Standard, specific, and generic rights.

    See:

    * https://learn.microsoft.com/en-us/windows/win32/secauthz/access-mask
    * https://learn.microsoft.com/en-us/windows/win32/secauthz/access-mask-format
    * https://learn.microsoft.com/en-us/windows/win32/secauthz/generic-access-rights
    """

    # fmt: off
    GENERIC_ALL     = 0x10000000
    GENERIC_EXECUTE = 0x20000000
    GENERIC_WRITE   = 0x40000000
    GENERIC_READ    = 0x80000000
    # fmt: on


class FILE_SHARE(IntFlag):
    """Sharing mode of a file or device.

    See: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
    """

    # fmt: off
    NONE   = 0x00000000
    READ   = 0x00000001
    WRITE  = 0x00000002
    DELETE = 0x00000004
    # fmt: on
