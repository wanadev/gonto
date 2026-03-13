Frequently Asked Questions
==========================

How to fix encoding error?
--------------------------

On Windows the console encoding may not be specified when running as service accounts (e.g. GitLab CI). This can lead to unicode encoding errors exceptions::

    UnicodeEncodeError: 'charmap' codec can't encode characters in position 18-24: character maps to <undefined>

To fix this error, you can force UTF-8 encoding using the ``PYTHONIOENCODING=utf-8`` environment variable before running Gonto.

Powershell:

.. code-block:: ps1

   $env:PYTHONIOENCODING=utf-8
   .\gonto.exe ...

CMD.exe:

.. code-block:: bat

   set PYTHONIOENCODING=utf-8
   .\gonto.exe ...
