Gonto – Dependency manager for WanadevStudio
============================================

.. figure:: ./gonto.png
   :alt: Gonto Logo


Requirements
------------

* Python >= 3.10


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

Then you can build the documntation with the following command::

    nox -s gendoc

Result goes to ``build/html/``.


.. _Nox: https://nox.thea.codes/


Changelog
---------

* **[NEXT]** (changes on ``master``, but not released yet):

  * Nothing yet ;)
