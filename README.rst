TeeTime
=======

.. image:: https://travis-ci.com/Peilonrayz/teetime.svg?branch=master
   :target: https://travis-ci.com/Peilonrayz/teetime
   :alt: Build Status

About
-----

Adding tee like functionally to ``subprocess.Popen``.

Installation
------------

.. code:: shell

   $ python -m pip install teetime

Documentation
-------------

Documentation is available `via GitHub <https://peilonrayz.github.io/teetime/>`_.

Basic Usage
-----------

Common usage is:

.. code:: python

   import sys
   import teetime

   with open('log.txt', 'wb') as f:
      process = teetime.popen_call(
         ['python', 'test.py'],
         stdout=(sys.stdout.buffered, f),
         stderr=(sys.stderr.buffered, f),
      )
      process.wait()

**Note**: ``popen_call`` blocks until IO is complete. If you have no IO, ``stdout=()``, then it will not block. This is why you still need ``process.wait()``.

Testing
-------

To run all tests run ``nox``. No venv is needed; nox makes all of them for us.

.. code:: shell

   $ python -m pip install --user nox
   $ git clone https://peilonrayz.github.io/teetime/
   $ cd teetime
   teetime $ nox

License
-------

TeeTime is available under the MIT license.
