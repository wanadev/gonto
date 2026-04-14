Gonto – Dependency manager for WanadevStudio
============================================

Gonto is a tool we developed to handle our multiple Unreal Engine versions on our CI and our developers' PCs. It can automatically download our UE versions (and some other dependencies like Android SDK with its associated JDK) from our centralised repository, prepare the environment and run our build scripts.

Gonto handles dependencies as disk images, mounts them on Windows drive letters (for example ``U:\\``) and adapts the environment and registry to point to the right places. Using disk images allows us to directly use the dependencies without having to extract them.

When you have a Zip, you need twice the disk space (for the Zip itself and the extracted files), and it can take hours to extract (a complete Unreal Engine build contains more than 200 000 files and requires more than 140 GiB of disk space).

Features:

* Dependency management (download and cache on disk).
* Centralised repository (any HTTP server with a specific file organization).
* Targets, like a *Makefile* (e.g. ``"build-windows"``, ``"build-android"``, ``"build-meta"``, ``"build-playstation"``,...).
* Complete pipeline execution with the ``"gonto run <TARGET>"`` command (download images missing from the cache, mount all dependencies and update environment, run build script, cleanup).
* A way to permanently mount the dependencies of a specific target without running the script (for developers' PCs): ``"gonto mount <TARGET>"``.
* A command to create a disk image from a source folder: ``"gonto create <SOURCE_FOLDER> <DEST_IMAGE>.vhd"``.

.. figure:: ./doc/_static/gonto-logo.256.png
   :alt: Gonto Logo


Requirements
------------

* Windows 10 or Windows 11
* Python >= 3.11 (for the source code version, standalone builds do not require any Python installation)


Usage
-----

Example Gonto config:

.. code-block:: yaml

    gonto:

      cache_dir: "W:\\gonto-cache\\"
      repository: "https://example.org/gonto-repo/"

    targets:

      build-windows:
        requires:
          - name: "unreal"
            version: "5.4.0"
            env:
              UNREAL_PATH: "{{mount_point}}"
            reg:
              - root: "HKEY_CURRENT_USER"
                path: "Software\\Epic Games\\Unreal Engine\\Builds"
                name: "5.4"
                data: "{{mount_point}}"
        script: |
          .\build.bat --target=windows

      build-android:
        requires:
          - name: "unreal"
            version: "5.4.0"
            env:
              UNREAL_PATH: "{{mount_point}}"
          - name: "android"
            version: "36"
            env:
              ANDROID_HOME: "{{mount_point}}android\\"
              JAVA_HOME: "{{mount_point}}java\\JDK25\\"
        script: |
          .\build.bat --target=android

List available targets::

    gonto.exe list

Run a target::

    gonto.exe run build-windows

Download and mount dependencies from a target::

    gonto.exe mount build-android

Create a new disk image from a folder::

    gonto.exe create --label "UE 5.5 Custom" ".\build_output" unreal_v5.5-custom1_win64.vhd


Documentation
-------------

* https://wanadev.github.io/gonto/


Contributing
------------

Lint and test the code
~~~~~~~~~~~~~~~~~~~~~~

You must install Nox_ first::

    pip3 install nox

Then you can check for lint errors::

    nox -s lint

Run the tests::

    nox -s test

And you can fix coding style errors automatically with::

    nox -s black_fix


Build the documentation
~~~~~~~~~~~~~~~~~~~~~~~

You must install Nox_ first::

    pip3 install nox

Then you can build the documentation with the following command::

    nox -s gendoc

The result goes to ``build/html/``.


.. _Nox: https://nox.thea.codes/


Changelog
---------

* **[NEXT]** (changes on ``master``, but not released yet):

  * feat: Added "create" command to create VHDs from a folder
  * feat: Improved error/success reporting
  * feat: Improved titles drawing
  * fix(main): Do not read config for "create" command
  * fix(mount): Try to detach all disk images if mount fails

* **v0.2.0:**

  * feat: Added "mount" command to download and permanently mount target images
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
