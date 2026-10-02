#!/usr/bin/env python3

import sys
import time
import tempfile

from gonto.diskimage import DiskImage
from gonto.win32.virtdisk import ATTACH_VIRTUAL_DISK_FLAG


def print_help():
    print("USAGE:")
    print("  ./diskimage_custom_path.py <DISK_IMAGE>")


def main(args=sys.argv[1:]):
    if len(args) != 1:
        print_help()
        sys.exit(1)

    disk = DiskImage()

    print("Opening disk image...")
    disk.open(args[0])

    print("Attaching disk image...")
    disk.attach(attach_flags=ATTACH_VIRTUAL_DISK_FLAG.NO_DRIVE_LETTER)

    with tempfile.TemporaryDirectory() as tempdir_name:

        # Path MUST end with a backslash
        if tempdir_name[-1] != "\\":
            tempdir_name += "\\"

        print("Mounting volume to '%s'..." % tempdir_name)
        disk.mount_volume(tempdir_name)

        time.sleep(2)

        # print("Unmounting volume...")
        # disk.umount_volume(mount_point=tempdir_name)

        print("Detaching disk image...")
        disk.detach()


if __name__ == "__main__":
    main()
