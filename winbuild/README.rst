Build Gonto for Windows
=======================

This document explain how to compile the Gonto Python code for Windows and
how to generate the release ZIP.

The compiled code is standalone, there is no need to install Python or other
dependency on the target system.


Requirements
------------

To build Gonto for Windows, you must first install the following
dependencies:

* Windows 11:

  * Download (VM): https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/

* Install Chocolatey (optional, but simpler setup):

  * Run in PowerShell as administrator:
    ``Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))``
  * NOTE: all ``choco`` commands should be run as administrator

* Python 3.11:

  * 64bit version
  * Must be added to the PATH (there is a checkbox during the installation)
  * Virtualenv must be installed and available in the PATH too
  * Download: https://www.python.org/
  * Choco: ``choco install python``

* Git:

  * Download: https://git-scm.com/
  * Choco: ``choco install git``

* Visual Studio 17 (2022)

  * Already installed in the Windows 11 Dev VM, else use Chocolatey
  * Choco: ``choco install visualstudio2022-workload-vctools``

Restart to finish setup.


Compile Gonto
-------------

Run the following command from the project's root directory (the one that
contains the ``pyproject.toml`` file)::

    winbuild\build.bat

The result goes to ``gonto-win.dist`` folder.


Build distribuable files
------------------------

* Zip: run ``winbuild\build-zip.bat``

Results goes to the ``dist``  folder.
