.. _install:

Installing hackeeg
==================


This part of the documentation covers the installation of hackeeg.
The first step to using any software package is getting it properly installed.


$ pipenv install hackeeg
------------------------

To install hackeeg, run this command in your terminal of choice::

    $ pipenv install
    $ pipenv install hackeeg
    $ pipenv shell

If you don't have `pipenv <https://pipenv.kennethreitz.org/en/latest/>`_ installed, head over to the 
`Pipenv website <https://pipenv.kennethreitz.org/en/latest/>`_ for installation instructions. Or, if 
you prefer to just use pip and don't have it installed,
`this Python installation guide <https://pip.pypa.io/en/stable/installing/>`_
can guide you through the process.

Get the Source Code
-------------------

hackeeg is actively developed on GitHub, where the code is
`always available <https://github.com/starcat-io/hackeeg-client-python>`_. If you want
to modify it or help us develop it, you'll need the source code.

You can either clone the public repository::

     $ git clone git://github.com/starcat-io/hackeeg-client-python

Or, download the `tarball <https://github.com/starcat-io/hackeeg-client-python/tarball/master>`_::

     $ curl -OL https://github.com/starcat-io/hackeeg-client-python/tarball/master
     # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your own Python
package, or install it into your site-packages easily::

    $ cd hackeeg-client-python
    $ pip install .

