#!/usr/bin/env python3

import sys
import time

from gonto.win32 import virtdisk


def print_help():
    print("USAGE:")
    print("  ./win32_virtdisk.py <DISK_IMAGE>")


def main(args=sys.argv[1:]):
    if len(args) != 1:
        print_help()
        sys.exit(1)

    vd = virtdisk.VirtDisk()

    print("Opening disk image...")
    vd.open(args[0])

    print("Attaching disk image...")
    vd.attach()

    phy_path = vd.get_physical_path()
    print("Physical path: %s" % phy_path)

    time.sleep(2)

    print("Detaching disk image...")
    vd.detach()


if __name__ == "__main__":
    main()
