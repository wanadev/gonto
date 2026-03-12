Things to do when releasing a new version
=========================================

This file is a memo for the maintainer.


0. Checks
---------

* Check copyright years in ``doc/conf.py``
* Check copyright years in ``LICENSE.txt``


1. Release
----------

* Update version number in ``pyproject.toml``
* Update version number in ``gonto/__init__.py``
* Edit / update changelog in ``README.rst``
* Commit / tag (``git commit -m vX.Y.Z && git tag vX.Y.Z && git push && git push --tags``)


2. Build Windows standalone version
-----------------------------------

* Follow instructions of ./winbuild/README.rst


3. Misc
-------

* Update Gonto on ``winbuild2``
* Update Gonto on ``winbuild3``
