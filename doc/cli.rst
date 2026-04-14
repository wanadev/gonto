Command Line
============

Gonto is a command line application. You can run it from CMD.exe or Powershell. To get help::

    gonto.exe --help

The Gonto command line is composed of different subcommands. General CLI usage::

    gonto.exe <subcommand> [options]


Main CLI (no subcommand)
------------------------

::

    usage: gonto.exe [-h] [-v] {list,run,mount,create} ...

    positional arguments:
      {list,run,mount,create}
        list                lists available targets
        run                 runs the requested target
        mount               mount disk images of the given target (without running scripts)
        create              create a new disk image with given content

    options:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

Example::

    gonto.exe --version


"list" Subcommand
-----------------

Lists available targets. This subcommand requires a configuration file.

::

    usage: gonto.exe list [-h]

    options:
      -h, --help  show this help message and exit

Example::

    gonto.exe list


"run" Subcommand
----------------

Downloads and mounts dependencies, then runs the scripts of the given target. This subcommand requires a configuration file.

::

    usage: gonto.exe run [-h] target

    positional arguments:
      target      the target to run

    options:
      -h, --help  show this help message and exit

Example::

    gonto.exe run windows-build


"mount" Subcommand
------------------

Downloads and permanently mounts dependencies of the given target without running scripts. This subcommand requires a configuration file.

::

    usage: gonto.exe mount [-h] target

    positional arguments:
      target      the target whose images will be mounted

    options:
      -h, --help  show this help message and exit

Example::

    gonto.exe mount windows-build


"create" Subcommand
-------------------

Creates a new disk image provisioned with the content of the input folder.

::

    usage: gonto.exe create [-h] [-p SPACE] [-l LABEL] INPUT_FOLDER OUTPUT_IMAGE

    positional arguments:
      INPUT_FOLDER          path of the folder that contains files to copy into the disk image
      OUTPUT_IMAGE          path of the output image file

    options:
      -h, --help            show this help message and exit
      -p SPACE, --overprovisioning SPACE
                            additional disk space to provision (in GiB)
      -l LABEL, --label LABEL
                            label of the disk image (default: 'Gonto image')

Simple example::

    gonto.exe create input_folder\ output_image.vhd

With a custom volume label::

    gonto.exe create --label "My Label" input_folder\ output_image.vhd

With 4 GiB of additional space in the disk image::

    gonto.exe create --overprovisioning 4 input_folder\ output_image.vhd
