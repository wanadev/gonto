#!/usr/bin/env python3

import sys
import time

from gonto.diskimage import DiskImage


def print_help():
    print("USAGE:")
    print("  ./diskimage.py <DISK_IMAGE>")


def main(args=sys.argv[1:]):
    if len(args) != 1:
        print_help()
        sys.exit(1)

    disk = DiskImage()

    print("Opening disk image...")
    disk.open(args[0])

    print("Attaching disk image...")
    disk.attach()

    phy_path = disk.get_physical_path()
    print("Physical path: %s" % phy_path)

    for vol in disk.list_volumes():
        print("Volume: %s" % vol)

    time.sleep(2)

    print("Detaching disk image...")
    disk.detach()


if __name__ == "__main__":
    main()
