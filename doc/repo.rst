Gonto Repository
================

Gonto can download disk images from a repository to fulfill requirements of a target.


Disk Image provisioning
-----------------------

When Gonto runs a task, it will start by checking if required disk images are available in its cache folder (configured in ``gonto.cache_dir`` key of the :ref:`gonto configuration`). If the disk image is not in the cache, it will download if from the repository (configured in ``gonto.repository`` key of the :ref:`gonto configuration`).

Once all required images available in the cache, Gonto will mount them on drive letters.


Repository Specifications
-------------------------

A Gonto repository is simply an HTTP server with files organized in the following way::

    /<name>/<name>_v<version>_<platform>.<format>

Where:

* ``<name>`` is the name of the disk image (``[a-z0-9-]+``, no space, no underscore,
  lowercase),

* ``<version>`` is the version of the disk image (``[0-9]+(\.[0-9]+)*(-[a-z0-9]+)?``
  → ex: ``160``, ``1.2.3``, ``1.2.3-beta1``, ``1.2.3-custom1``),

* ``<platform>`` is the target platform of the disk image (``win32``, ``win64`` or ``multi``),

* ``<format>``: is the format of the disk image (``vhd`` or ``vhdx``).

Example::

    https://example.org/gonto-repo/unreal/unreal_v5.4.1-custom1_win64.vhd
