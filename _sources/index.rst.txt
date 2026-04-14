Gonto documentation
===================

Gonto is a tool we developed to handle our multiple Unreal Engine versions on our CI and our developers' PCs. It can automatically download our UE versions (and some other dependencies like Android SDK with its associated JDK) from our centralised repository, prepare the environment and run our build scripts.

Gonto handles dependencies as disk images, mounts them on Windows drive letters (for example ``U:``) and adapts the environment and registry to point to the right places. Using disk images allows us to directly use the dependencies without having to extract them.

When you have a Zip, you need twice the disk space (for the Zip itself and the extracted files), and it can take hours to extract (a complete Unreal Engine build contains more than 200 000 files and requires more than 140 GiB of disk space).

Features:

* Dependency management (download and cache on disk).
* Centralised repository (any HTTP server with a specific file organization).
* Targets, like a *Makefile* (e.g. ``"build-windows"``, ``"build-android"``, ``"build-meta"``, ``"build-playstation"``,...).
* Complete pipeline execution with the ``"gonto run <TARGET>"`` command (download images missing from the cache, mount all dependencies and update environment, run build script, cleanup).
* A way to permanently mount the dependencies of a specific target without running the scripts (for developers' PCs): ``"gonto mount <TARGET>"``.
* A command to create a disk image from a source folder: ``"gonto create <SOURCE_FOLDER> <DEST_IMAGE>.vhd"``.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   ./cli.rst
   ./config.rst
   ./repo.rst
   ./env.rst
   ./faq.rst
   ./python_api/index.rst
   ./winbuild.rst
