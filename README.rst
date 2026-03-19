Gonto – Dependency manager for WanadevStudio
============================================

.. figure:: ./gonto.png
   :alt: Gonto Logo


Requirements
------------

* Python >= 3.11


Documentation
-------------

* https://pages.wanadev.org/tools/gonto/


Contributing
------------

Lint the code
~~~~~~~~~~~~~

You must install Nox_ first::

    pip3 install nox

Then you can check for lint error::

    nox -s lint

And you can fix coding style errors automatically with::

    nox -s black_fix


Build the documentation
~~~~~~~~~~~~~~~~~~~~~~~

You must install Nox_ first::

    pip3 install nox

Then you can build the documentation with the following command::

    nox -s gendoc

Result goes to ``build/html/``.


.. _Nox: https://nox.thea.codes/


Changelog
---------

* **[NEXT]** (changes on ``master``, but not released yet):

  * feat: Added "mount" command to download and permanently mount targets images
  * feat: Added "reg" option to requirements allowing to set registry key after mounting disk images

* **v0.1.1:**

  * fix(download): Do not continue running target on incomplete download
  * misc(winbuild): Build with unbuffered output option

* **v0.1.0 (initial release):**

  * feat: Multiple config files with overrides (``gonto.yaml``)
  * feat: List targets (``gonto list``)
  * feat: Run target (``gonto run <TARGET>``):

    * Download missing VHDs from a repository
    * VHD cache
    * Mount/Unmount VHDs
    * before_script/script/after_script
    * Handle environment variable with dynamic replacement of the mount point
