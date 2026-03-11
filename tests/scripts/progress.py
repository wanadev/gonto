#!/usr/bin/env python3

import time

from gonto.clihelpers import ProgressBar


def main():
    pb = ProgressBar(text="Downloading 'foobar.vhd'...")
    pb.start()
    for i in range(1001):
        pb.update(i / 1000)
        time.sleep(0.01)
    pb.finish()


if __name__ == "__main__":
    main()
