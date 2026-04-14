Things to do when releasing a new version
=========================================

This file is a memo for the maintainer.


0. Checks
---------

* Check copyright years in ``doc/conf.py``


1. Release
----------

* Update version number in ``pyproject.toml``
* Update version number in ``gonto/__init__.py``
* Edit / update changelog in ``README.rst``
* Commit / tag (``git commit -m vX.Y.Z && git tag vX.Y.Z && git push && git push --tags``)


2. Publish package on PyPI
--------------------------

Automated, nothing to do.


3. Build Windows standalone version
-----------------------------------

Automated (built on CI), just download the artifact once finished.


4. Publish release
------------------

* Make a release on GitHub
* Add standalone zip
